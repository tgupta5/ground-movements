import json

###############################################################################
##                          Classify SFO Gates                               ##
###############################################################################
## Requester:                              United Airlines Ground Ops
## Documentation: https://www.flightaware.com/aeroapi/portal/documentation#overview
## Created by:    Tanay Gupta
## Created by:
## Created by:
##
''' Purpose:
Help United optimize aircraft gating at SFO Airport. 
This application will first classify all of the United-accessible gates
based on allowable aircraft types and then develop optimization algorithm
that reflects bank and lull periods.

'''
##-----------------------------------------------------------------------------
##                            Source tables                                  ##
##-----------------------------------------------------------------------------
##      Using aero API's GET /flights/{ident}
##
##
##----------------------------------------------------------------------------- 
##                         calcs/business rules                              ##
##-----------------------------------------------------------------------------
##
##
##
##-----------------------------------------------------------------------------
##                             CHANGE LOG                                    ##
##-----------------------------------------------------------------------------
## DATE | FIRST NAME | LAST NAME      |CHANGE MADE
## 12/15                Gupta           init
##
###############################################################################


###############################################################################
##                          Step 1: Get Flights at SFO                       ##
###############################################################################

'''
Establish data structure: Nested Dictionary 

gate_info = {
    'Gate1': {'Boeing 737': 3, 'Airbus A320': 2},
    'Gate2': {'Boeing 737': 1, 'Boeing 777': 4},
    # ... (other gates)
}
'''
file_path = 'sfo_aircraft_response.json'
all_sfo_flights = ""
with open(file_path, 'r') as json_file:
    all_sfo_flights = json.load(json_file)

gate_inventory_dict = {}

'''
structure is:
"arrivals":
    0:
        "identifier"
        "aircraft_type"
        "gate_origin"
        "gate_destination"
"departures":
    0:
        "identifier"
        "aircraft_type"
        "gate_origin"
        "gate_destination"
'''

for flight_movement_list in all_sfo_flights:  ## "arrivals", "departures", "scheduled arrivals"...

    for arr_or_departure in flight_movement_list:
    ## First get the gate and aircraft type
        if arr_or_departure == 'arrivals':  ## arriving into SFO
            curr_sfo_gate = flight_movement_list['arrivals']['gate_destination']
        elif arr_or_departure == 'departures':  ## departing from SFO
            curr_sfo_gate = flight_movement_list['departures']['gate_origin']
        else:
            continue  ## only want actual arrivals and departures, not links or scheduled ish

        curr_aircraft = flight_movement_list["aircraft_type"].strip()
        

        '''
        if gate (G3) exists,
            if aircraft type (B737) exists at G3:
                increment that aircraft's appearance ctr
            else:
                add that aircraft type with a ct of 1
        else:
            add that gate

        ''' 
        if curr_sfo_gate in gate_inventory_dict:
            aircraft_at_gate_dict = gate_inventory_dict[curr_sfo_gate]

            if str(curr_aircraft) in aircraft_at_gate_dict:     
                    aircraft_at_gate_dict[str(curr_aircraft)] += 1
            
            else:  ## aircraft type not visited this gate yet
                    aircraft_at_gate_dict[str(curr_aircraft)] = 1

        else:  ## gate not yet in this dict
                gate_inventory_dict[curr_sfo_gate] = {str(curr_aircraft): 1}

    # gate_inventory_dict.setdefault(curr_gate, set()).add(curr_aircraft)

print(gate_inventory_dict)

