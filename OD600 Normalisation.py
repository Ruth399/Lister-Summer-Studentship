import json
from opentrons import protocol_api, types

metadata = {
    "protocolName": "OD600 Normalisation",
    "author": "Ruth Legesse",
    "description": "Normalise OD600 values to a target value"
}

requirements = {"robotType": "Flex", "apiLevel": "2.29"}

def add_parameters(parameters: protocol_api.ParameterContext):
    parameters.add_csv_file(
        variable_name = "od600_data",
        display_name = "OD600 Normalisation",
        description = "CSV with well_position, BHI_volume, and stock_bacteria_volume columns from the KNIME pathway"
    )

def run(protocol: protocol_api.ProtocolContext) -> None:  #we are defining "protocol", and using the type hint to specify that it is a ProtocolContext object. This allows us to use the methods and attributes of the ProtocolContext class within the function.
    heater_shaker_module_1 = protocol.load_module("heaterShakerModuleV1", "D1") #the dot notation means that we are accessing the load_module method of the protocol object, which is an instance of the ProtocolContext class. The load_module method takes two arguments: the name of the module to load and the location on the deck where it should be placed. In this case, we are loading a heater-shaker module and placing it in slot D1.
  
        tip_rack_1 = protocol.load_labware(
            "opentrons_flex_96_filtertiprack_1000ul",
            location = "A1",
            namespace = "opentrons"
            version = 1,
        ) 

        tip_rack_2 = protocol.load_labware(
            "opentrons_flex_96_filtertiprack_1000ul",
            location = "A3",
            namespace = "opentrons",
            version = 1,
                )   
    #the load_labware  method takes several arguments: the name of the labware to load, the location on the deck where it should be placed, an optional label for the labware, the namespace of the labware definition (this specifies whether the labware belongs to the pre-established library or was instead custom added with a JSON file), and the version of the labware definition. In this case, we are loading a tip rack and placing it in slot C2.
        stock_bacteria = protocol.load_labware(
            "corning_96_wellplate_330ul",
            location = "B1",
            namespace = "opentrons",
            version = 1,
            label = "Bacteria plate from which OD values were recorded",
    )

        BHI_media = protocol.load_labware(
            "corning_96_wellplate_330ul",
            location = "B3",
            namespace = "opentrons",
            version = 1,
            label = "Fresh BHI cell medium",
    )

        normalised_bacteria = protocol.load_labware(
            "corning_96_wellplate_330ul",
            location = "C1",
            namespace = "opentrons",
            version = 1,
            label = "Destination plate for the OD600 normalised bacteria",
        )

        waste_chute = protocol.load_waste_chute()
        #no need to specify position, as this is fixed - always going to be D3 on the Flex deck 

        
        pipette = protocol.load_instrument(
        "flex_8channel_1000", "left", tip_racks = [tip_rack_1]
        )

        #again, another method, load_instrument -> this takes two arguments: the name of the instrument to load and the mount on which it should be placed. In this case, we are loading a Flex 8-channel pipette with a maximum volume of 50 µL and placing it on the left mount.

        pipette.configure_nozzle_layout(
            style = protocol_api.SINGLE,
            start = "A1",
            tip_racks = [tip_rack_1],
        )

        #We have an 8-channel pipette, but can only use one at a time as the volumes we are transferring vary between wells.

        csv_file = protocol.params.od600_data #protocol.params is a read-only dictionary that contains all of the parameters that have been added to the protocol. In this case, we are accessing the od600_data parameter that was added in the add_parameters function. This parameter is a CSV file that contains the well positions, BHI volumes, and stock bacteria volumes for each sample.
        rows = csv_file.parse_as_csv()
        #using parse_as_csv() method to convert the table into a list of lists, where each inner list represents a row in the CSV file. The first set of [] will contain the headers.
        header, *data_rows = rows 
        #once the csv is parsed, we can separate the header from the data rows by assigning the first [] to header and everything else (demarked by the *) to data_rows

        for well_position, BHI_volume, stock_bacteria_volume in data_rows:
            BHI_volume = float(BHI_volume) 
            #the values in the csv will be converted into strings following parse_as_csv(), this reverts them back into float so that they can be used in the pipette transfer method.
            pipette.aspirate(BHI_volume, BHI_media[well_position])
            pipette.dispense(BHI_volume, normalised_bacteria[well_position])
        pipette.drop_tip(waste_chute)

        for well_position, BHI_volume, stock_bacteria_volume in data_rows:
            stock_bacteria_volume = float(stock_bacteria_volume)
            pipette.aspirate(stock_bacteria_volume, stock_bacteria[well_position])
            pipette.dispense(stock_bacteria_volume, normalised_bacteria[well_position])
        pipette.drop_tip(waste_chute)


