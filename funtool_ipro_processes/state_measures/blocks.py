import funtool.state_measure

@funtool.state_measure.state_and_parameter_measure
def count(state,parameters):
    state_xml_string= state.data.get(parameters.get('xml','xml'))
    if state_xml_string is None:
        return None
    else:
        return sum([state_xml_string.count(block) for block in parameters.get('blocks')]) 
