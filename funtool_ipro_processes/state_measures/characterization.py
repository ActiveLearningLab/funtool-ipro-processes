import funtool.state_measure
import math
import itertools

@funtool.state_measure.state_and_parameter_measure
def characterization(state,parameters):
    state_vector= { component: state.measures.get(count_variable,0) for (count_variable,component) in parameters.get('variables',{}).items() }
    characterization=[]
    if not ( None in state_vector.values()):
        state_norm= math.sqrt(sum([i*i for i in state_vector.values()]))
        if state_norm > 0:
            sorted_components= sorted(state_vector.items(), key=lambda x: x[1], reverse=True)
            characterization.append(sorted_components[0][0])
            if ( sorted_components[0][1] - sorted_components[1][1] )/state_norm < parameters.get('secondary_cutoff',0):
                characterization.append(sorted_components[1][0])
                if ( sorted_components[0][1] - sorted_components[2][1])/state_norm < parameters.get('tertiary_cutoff',0):
                    characterization.append(sorted_components[2][0])
    return _possible_characterizations(list(state_vector.keys())).index(tuple(sorted(characterization)))


def _possible_characterizations(components):
    sorted_components= sorted(components)
    return [ characterization for l in range(len(sorted_components) + 1) for characterization in itertools.combinations(sorted_components, l) ]
