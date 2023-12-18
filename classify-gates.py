import json  # reading json
import pandas as pd  # outputing as csv
import csv  # reading csv

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
that reflects bank and trough periods.

'''
##-----------------------------------------------------------------------------
##                            Source tables                                  ##
##-----------------------------------------------------------------------------
##   Using AeroAPI's GET airports/{id}/flights
##   Saving sample json wo using credits
##
##----------------------------------------------------------------------------- 
##                         calcs/business rules                              ##
##-----------------------------------------------------------------------------
##
##
##----------------------------------------------------------------------------- 
##                         fn call hierarchy                                 ##
##-----------------------------------------------------------------------------
##
##      main()
##          get_all_flights()
##              update_gate_dict()
##              augment_output_gate_dict()
##
##
##-----------------------------------------------------------------------------
##                             CHANGE LOG                                    ##
##-----------------------------------------------------------------------------
## DATE             | NAME    |CHANGE MADE
## 12/15 7:30p PT     Gupta    Added json and dict tracking aircraft type by 
##                               gate
##
###############################################################################

## TODO troubleshoot lookup csv file
## TODO gather more time periods of data

'''
Establish global Nested Dictionary storing aircraft type frequency by gate 

gate_info = {
    'Gate1': {'Boeing 737': 3, 'Airbus A320': 2},
    'Gate2': {'Boeing 737': 1, 'Boeing 777': 4},
    # ... (other gates)
}
'''
gate_inventory_dict = {}


###############################################################################
##                 Step 3: Sort + Expand Aircraft Type + Output              ##
###############################################################################

def augment_output_gate_inventory():
    """
    Take gate inventory from SFO API; sort, expand aircraft types, and output to csv
    """
    
    # Sort the outer keys (gate names) alphabetically
    sorted_outer_keys = sorted(gate_inventory_dict.keys())

    # Sort the inner dictionaries (aircraft types) alphabetically based on keys
    # TODO getting an UNBOUND LOCAL VARIABLE ERR if I do not recreate a new local variable
    sorted_gate_inventory_dict = {gate: dict(sorted(gate_inventory_dict[gate].items())) for gate in sorted_outer_keys}


    # merge in the full name of aircraft type
    path_to_lookup = 'data/lookup/aircraft_type_lookup.csv'
    aircraft_lookup_df = pd.read_csv(path_to_lookup)

    # FAA_Designator *Boeing B767-200* Model_FAA *Boeing B767-200*
    aircraft_lookup_dict = {}
    for idx,curr_aircraft in aircraft_lookup_df.iterrows():
        key = curr_aircraft['FAA_Designator']
        value = curr_aircraft['Model_FAA']
        aircraft_lookup_dict[key] = value

    ## Apply this new lookup to expand aircraft types in SFO dictionary
    ## New gate inventory dict will have {{G18: {Boeing B757-200,2}, ...}}
    expanded_gate_inventory_dict = {}
    for gate, aircraft_appearances in sorted_gate_inventory_dict.items():

        # temp store nested {aircraft:freq}
        expanded_aircraft_appearances = {}
        for curr_aircraft_type, freq in aircraft_appearances.items():
            full_aircraft_name = aircraft_lookup_dict[curr_aircraft_type]

            # if we already have that aircraft type at this gate
            if aircraft_lookup_dict.get(curr_aircraft_type):  
                expanded_aircraft_appearances[full_aircraft_name] = freq
            
            # if we don't, then on existing this for-loop it will get added

        expanded_gate_inventory_dict[gate] = expanded_aircraft_appearances

    # explicitly delete old gate inventory
    # del gate_inventory_dict, sorted_gate_inventory_dict, aircraft_lookup_df

    # output df to excel or throw an error
    try:

      # Path to the output text file
        output_file_path = 'data/out/gate_types.txt'

        # Open the text file in write mode
        with open(output_file_path, 'w') as file:
            # Loop through each key-value pair in the nested dictionary
            for key, inner_dict in expanded_gate_inventory_dict.items():
                file.write(f"{key}:\n")
                
                # Loop through each item in the inner dictionary and write it to the file
                for inner_key, value in inner_dict.items():
                    file.write(f"    {inner_key}: {value}\n")
                
                # Write a newline to separate each outer dictionary entry
                file.write('\n')

        print(f"Output has been written to '{output_file_path}'")

        # df = pd.DataFrame.from_dict(sorted_gate_inventory_dict, orient = "index")
        # output_path = "data/out/sfo_gate_inventory.xlsx"
        # df.to_excel(output_path, index = True)

        # print(f"Data has been successfully written to '{output_path}'")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    return

###############################################################################
##           Step 2: Update dict based on aircraft and gate                  ##
###############################################################################

def update_gate_dict(aircraft_type, gate_num):
    """
    Update dictionary to include new inventory of aircraft count at a given gate

    Args:
    - aircraft_type (str): model of United aircraft in Get Flights API
    - gate_num (str): gate for arriving/departing aircraft

    Returns:
    None

    """
    global gate_inventory_dict

    '''
    if gate (G3) exists,
        if aircraft type (B737) exists at G3:
            increment that aircraft's appearance ctr
        else:
            add that aircraft type with a ct of 1
    else:
        add that gate

    ''' 
    if gate_num in gate_inventory_dict:

        if aircraft_type in gate_inventory_dict[gate_num]:
            gate_inventory_dict[gate_num][aircraft_type] += 1
        
        else:  ## dict does not include this aircraft_type at this gate yet
            gate_inventory_dict[gate_num][aircraft_type] = 1

    else:  ## gate not yet in this dict
            gate_inventory_dict[gate_num] = {aircraft_type: 1}

    return


###############################################################################
##           Step 1: Get Flights arriving at or departing from SFO           ##
###############################################################################

def get_all_flights():
    """
    Take GET FLIGHTS json output from API call and access arriving and departing
      flights list. Call update_gate_dict() based on those parameters

    Args:
    None

    Returns:
    None

    """

    # get JSON data saved in repo
    file_path = 'data/in/sfo_aircraft_response.json'
    all_sfo_flights = ""
    with open(file_path, 'r') as json_file:
        all_sfo_flights = json.load(json_file)

    '''
    Get Flights JSON structure:
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

    for movement_type in all_sfo_flights:  ## "arrivals", "departures", "scheduled arrivals"...
        
        # for arrivals, get gate_destination; for departures, get gate_origin
        if movement_type == 'arrivals':  ## arriving into SFO
            for arriving_flight in all_sfo_flights['arrivals']:
                curr_arr_gate = arriving_flight['gate_destination']
                curr_aircraft = arriving_flight["aircraft_type"].strip()
                update_gate_dict(aircraft_type = curr_aircraft, gate_num = curr_arr_gate)

        elif movement_type == 'departures':  ## departing from SFO
            for departing_flight in all_sfo_flights['departures']:
                curr_departing_gate = departing_flight['gate_origin']
                curr_aircraft = departing_flight['aircraft_type'].strip()
                update_gate_dict(aircraft_type = curr_aircraft, gate_num = curr_departing_gate)
            
        else:
            continue  ## only want actual arrivals and departures, not links or scheduled ish

    ## take gate inventory and prep for output
    augment_output_gate_inventory()

    print(gate_inventory_dict)

    return

def main():
    get_all_flights()


if __name__ == "__main__":
     main()  # Execute the main function when the script is run directly
