import os
from pandas import ExcelFile
import logging
import json
from xlrd import XLRDError
from math import isnan

# TODO: Add flag to preety print json
# TODO: Add flag to extact common json
# TODO: Add flag to process spreadsheets by regex
# TODO: Add flag to process a single spreadsheet
# TODO: Add flag to set value on elements with missing keys
# TODO: Add verbose flag

# Utility function to insert a value into a dictionary with key nesting.
# The dictionary represents the json file
# It takes a list of keys with each key list item being one level deeper
# than the last
def nestedInsertIntoDict(keys, value, dictionary, emptyDicts, emptyStrIdentifier):
    for i in range(len(keys) - 1):
        dictionary.setdefault(keys[i], {})
        if (type(dictionary[keys[i]]) == dict):
            dictionary = dictionary[keys[i]]
        else:
            # The key value is not a dictionary, but is should be. This is probably because the excel file
            # was changed incorrectly or because the starting json is malformed.
            # Overiting key with dictionary.
            dictionary[keys[i]] = {}
            dictionary = dictionary[keys[i]]

    # If the there is a value written in the place of that key in the excel file
    if type(value) == str or not isnan(value):
        # If the key is not the empty string identifier
        if (value != emptyStrIdentifier):
            # Write the value to the dictionary (json file)
            dictionary[keys[-1]] = value
        else:
            # The value is the empty string identifier
            # This is a replacement for the empty string ''
            # Writing the empty string identifier to the dictionary (json file)
            dictionary[keys[-1]] = ""
    else:
        # There is no value for this key in the excel file
        # Could have generated empty dicts for keys,
        # which would generate invalid json keys add current
        emptyDicts.append(keys[:-1])

# Function for processing a single excel worksheet
def processSheet(sheetName, excelFile, outputDir, separator, emptyStrIdentifier):
    # Parse the current worksheet
    data = excelFile.parse(sheetName)
    # Get the json file name from the top left cell
    jsonFileName = data.columns[0]
    logging.info("Processing {}".format(jsonFileName))

    # Process one language at a time
    for currentCol in range(1, len(data.columns)):
        # Current language
        language = data.columns[currentCol]
        keys = {}
        emptyDicts = []
        for currentRow in range(1, len(data.index)):
            # Read current key (always at column 0)
            jsonKey = data.iloc[currentRow][0]
            jsonKey = jsonKey.split(separator)
            # Try to write key value into json dict
            nestedInsertIntoDict(jsonKey, data.iloc[currentRow][currentCol], keys, emptyDicts, emptyStrIdentifier)
        # If the language directory doesn't exist, create it
        if not os.path.exists(os.path.join(outputDir, language)):
            os.mkdir(os.path.join(outputDir, language))
            logging.warning("Created directory {}".format(os.path.abspath(os.path.join(outputDir, language))))
        # If there is some value written for the current file for this language
        if (len(keys) > 0):
            for removeKeys in emptyDicts:
                try:
                    levels = []
                    removeJsonKeys = keys
                    for k in removeKeys:
                        levels.append(removeJsonKeys)
                        removeJsonKeys = removeJsonKeys[k]
                    if removeJsonKeys == {}:
                        levels.reverse()
                        removeKeys.reverse()
                        for index, level in enumerate(levels):
                            if len(level[removeKeys[index]]) < 2:
                                level.pop(removeKeys[index])
                            else:
                                break
                except KeyError:
                    pass
            # Check again if there is anything written for the current file in this language
            if (len(keys) > 0):
                # Open a file, and write the dictionary (json) to it
                with open(os.path.join(outputDir, language, jsonFileName), "w", encoding="utf-8") as json_file:
                    json.dump(keys, json_file, ensure_ascii=False, indent=4)

# The function for processing the actual excel file
def processFile(excelFilePath, outputDir, separator, emptyStrIdentifier, quiet):
    try:
        xls = ExcelFile(excelFilePath)
        for sheet_name in xls.sheet_names:
            processSheet(sheet_name, xls, outputDir, separator, emptyStrIdentifier)
    except XLRDError as e:
        if not quiet:
            logging.critical("The excel file path is an invalid excel file")
        else:
            raise e

# Main function
def fromExcelToJson(excelFilePath, outputDir=".", separator="/", emptyStrIdentifier="$JHEMPTY", verbose=False, quiet=False):
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    # Disable logging if quiet mode is true or set logging level if it is false
    if quiet:
        logging.disable(logging.CRITICAL)
    else:
        if verbose:
            logging.basicConfig(level=logging.INFO, format="%(message)s")
        else:
            logging.basicConfig(level=logging.WARNING, format="%(message)s")
    logging.warning("Starting to process file \"{}\"".format(os.path.abspath(os.path.join(os.getcwd(), excelFilePath))))
    processFile(excelFilePath, outputDir, separator, emptyStrIdentifier, quiet)
    logging.warning("Finished")

# If the file is being run directly (without the tool)
if __name__ == "__main__":
    import sys
    from . import processArgs
    # Call the main function with the processed command line arguments
    fromExcelToJson(*processArgs.processExcelToJsonArgs(sys.argv[1:]))
