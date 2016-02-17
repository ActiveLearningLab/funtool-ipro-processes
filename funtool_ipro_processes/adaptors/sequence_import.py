import funtool.adaptor
import funtool.state
import funtool.state_collection

import pymysql
import pymysql.cursors

import yaml
import os

import datetime
import math

def sequence_import(adaptor, state_collection, overriding_parameters=None, logging=None):
    adaptor_parameters= funtool.adaptor.get_adaptor_parameters(adaptor,overriding_parameters)
    mysql_query= _prepare_query(adaptor_parameters)
    connection= _open_connection(_connection_values(adaptor_parameters.get('db_connection')))
    user_revisions={}
    start_time= datetime.datetime.strptime( adaptor_parameters.get('start_time'), "%Y-%m-%d %H:%M:%S" )
    stop_time= datetime.datetime.strptime( adaptor_parameters.get('stop_time'), "%Y-%m-%d %H:%M:%S" )
    time_step= int(adaptor_parameters.get('time_step'))
    time_slices= math.ceil( (stop_time - start_time).total_seconds()/time_step )
    all_rows=[]
    try:
        reader= _mysql_row(connection, mysql_query) 
        for row in reader:
            all_rows.append(row)
            user= row.get(adaptor_parameters.get('user_column','username'))
            characterization= row.get(adaptor_parameters.get('characterization_column','characterization'))
            time_slice= int(( row.get(adaptor_parameters.get('time_column'),'created_at') - start_time ).total_seconds())//time_step
            # Initialize for new user, time_slice
            user_revisions[user]= user_revisions.get(user,{})
            user_revisions[user][time_slice]= user_revisions[user].get(time_slice,[])

            user_revisions[user][time_slice].append(characterization)
    finally:
        connection.close()
    
    user_sequences= _create_sequences(user_revisions,time_slices,adaptor_parameters.get('trim_leading_none',False))

    return funtool.state_collection.StateCollection(states=_create_states_from_sequences(user_sequences), groupings={})

def _open_connection(connection_values):
    return pymysql.connect( **connection_values)


def _connection_values(adaptor_db_connection_parameters):
    conn_parameters= adaptor_db_connection_parameters.copy()
    config_file= conn_parameters.pop('config_file',None)
    yaml_config= None
    if not config_file is None:
        with open(config_file) as f:
            yaml_config= yaml.load(f)
    if yaml_config is None:
        yaml_config= {}
    yaml_config.update(conn_parameters)
    conn_parameters= yaml_config
    conn_parameters['cursorclass']= pymysql.cursors.DictCursor  # Forces the cursor to return Dicts
    return conn_parameters

def _mysql_row(connection, sql):
    with connection.cursor() as cur:
        cur.execute(sql)
        results= cur.fetchall()
        for result in results:
            yield result

def _prepare_query(adaptor_parameters):
    mysql_query= adaptor_parameters.get('SQL')
    if mysql_query is not None:
        where_clauses=[]
        order_by_clause= None
        if adaptor_parameters.get('teams',False):
            where_clauses.append( '\nOR '.join([ 
                adaptor_parameters.get('user_column','username') + ' LIKE \'' +team+'%\'' 
                for team in adaptor_parameters.get('teams',[])]))
        if adaptor_parameters.get('start_time',False):
            where_clauses.append(adaptor_parameters.get('full_time_column')+' > \'' + adaptor_parameters.get('start_time')+'\'')
        if adaptor_parameters.get('stop_time',False):
            where_clauses.append(adaptor_parameters.get('full_time_column')+' < \'' + adaptor_parameters.get('stop_time') +'\'')
        if adaptor_parameters.get('order_by'):
            order_by_clause ='ORDER BY ' + ', '.join(adaptor_parameters.get('order_by'))
        if len(where_clauses) > 0:
            mysql_query+= '\nWHERE '
            mysql_query+= 'AND '.join( [ '(' + clause + ')\n' for clause in where_clauses ] )
        if not(order_by_clause is None):
            mysql_query+= order_by_clause
    return mysql_query

def _create_sequences(user_timeslice_characterization, time_slices, trim_common_none=False):
    user_sequences= {}
    for user in user_timeslice_characterization.keys():
        user_sequences[user]= [ user_timeslice_characterization[user].get(0,[None])[-1] ]
        for time_slice in range(1,time_slices):
            user_sequences[user]= user_sequences[user] + [ user_timeslice_characterization[user].get(time_slice,user_sequences[user])[-1] ]
    if trim_common_none:
        print('trimming')
        first_not_none= min([ next( i for i,c in enumerate(sequence) if not( c is None) ) for sequence in user_sequences.values()])
        user_sequences= { user:sequence[first_not_none:] for user,sequence in user_sequences.items()}
    return user_sequences

def _create_states_from_sequences(user_sequences):
    return [ funtool.state.State(
                id=None,
                data={'sequence':sequence,'username':user},
                measures={},
                meta={},
                groupings={})
            for user,sequence in user_sequences.items() ]
