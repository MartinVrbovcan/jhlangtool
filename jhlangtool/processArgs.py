import getopt
import pkg_resources

# Helper function for parsing command line arguments
def parseArgs(argumentList, shortargs, longArguments, longOptionalArguments):
    # Preprocessing long command line paramaters as a workaround
    # for optional long arguments (getopt doesn't support optional long arguments)
    longArguments.extend([argument[2:]+"=" for argument in longOptionalArguments])
    for index, option in enumerate(argumentList):
        # Check if argument is in the list of optional arguments
        try:
            # Argument is in list, removing it from optional argument list
            longOptionalArguments.remove(option)
            try:
                if argumentList[index + 1][:1] == "-":
                    argumentList.insert(index+1, "")
            except IndexError:
                argumentList.append("")
        except ValueError:
            pass

    for argument in longOptionalArguments:
        argumentList.append(argument+"=")

    # Reurn processed args
    return getopt.gnu_getopt(argumentList, shortargs, longArguments)

# Function for processing valueless args (such as help, verbose, quiet...)
def processValuelessArguments(valuelessArgumentList, passedInArgs, argsDict, mapShortToLong):
    for v, _ in passedInArgs:
        try:
            argsDict[
                valuelessArgumentList[valuelessArgumentList.index(mapShortToLong.get(v.strip("-"), v.strip("-")))]
            ] = True
        except ValueError:
            pass

# Function to process command line arguments for the "generateExcel" utility
def processJsonToExcelArgs(argumentList):
    shortHelpText = pkg_resources.resource_string(__name__, "helpMessages/generateExcelShortHelp.txt").decode()
    try:
        # Process args and write them down
        options, arguments = parseArgs(argumentList, "hvqf:i:s:", ["help", "quiet", "verbose"], ["--filepath",
                             "--separator", "--identifier"])

        argumentsDict = {}
        mapShortToLong = {
            "f": "filepath",
            "s": "separator",
            "i": "identifier",
            "v": "verbose",
            "q": "quiet",
            "h": "help"
        }
        processValuelessArguments(["help", "quiet", "verbose"], options, argumentsDict, mapShortToLong)

        # If help is an argument, show the help texr and quit the program
        if "help" in argumentsDict.keys():
            print(pkg_resources.resource_string(__name__, "helpMessages/generateExcelLongHelp.txt").decode())
            quit()

        # If there is only one argument (the base directory path)
        if len(arguments) == 1:
            # Process arguments
            for o, v in options:
                if v != "":
                    argumentsDict[mapShortToLong.get(o.strip("-"), o.strip("-"))] = v

            # Return arguments as list
            return [arguments[0], argumentsDict.get("filepath", "./output.xlsx"),
                    argumentsDict.get("separator", "/"), argumentsDict.get("identifier", "$JHEMPTY"),
                    argumentsDict.get("verbose", False), argumentsDict.get("quiet", False)]
        # The base directory was not specified
        elif len(arguments) < 1:
            print("Missing path to base directory")
            print(shortHelpText)
            quit()
        else:
            # Too many arguments provided
            print("Too many arguments")
            print(shortHelpText)
            quit()
    except getopt.GetoptError as e:
        # Invalid option
        print("Invalid option {}".format(e.opt))
        print(shortHelpText)

# Function to process command line arguments for the "generateJsonFromExcel" utility
def processExcelToJsonArgs(arumentList):
    # Init helpText
    helpText = pkg_resources.resource_string(__name__, "helpMessages/excelToJsonHelp.txt").decode()
    try:
        # Process args and write them down
        options, arguments = parseArgs(arumentList, "hvqo:s:i:", ["help", "verbose", "quiet"], ["--output", "--separator", "--identifier"])
        argumentsDict = {}
        mapShortToLong = {
            "o": "output",
            "s": "separator",
            "i": "identifier",
            "v": "verbose",
            "q": "quiet",
            "h": "help"
        }
        processValuelessArguments(["help", "quiet", "verbose"], options, argumentsDict, mapShortToLong)

        # If help is an argument, show the help texr and quit the program
        if "help" in argumentsDict.keys():
            print(helpText)
            quit()

        # If there is only one argument (the path to the excel file)
        if len(arguments) == 1:
            # Process arguments
            for o, v in options:
                if (v != ""):
                    argumentsDict[mapShortToLong.get(o.strip("-"), o.strip("-"))] = v

            # Return arguments as list
            return [arguments[0], argumentsDict.get("output", "."), argumentsDict.get("separator", "/"),
                    argumentsDict.get("identifier", "$JHEMPTY"), argumentsDict.get("verbose", False),
                    argumentsDict.get("quiet", False)]
        # The path to the excel file was not specified
        elif len(arguments) < 1:
            print("Missing path to excel file")
            print(helpText)
            quit()
        else:
            # There are too many arguments
            print("Too many arguments")
            print(helpText)
            quit()


    except getopt.GetoptError as e:
        # Invalid option
        print("Invalid option {}".format(e.opt))
        print(helpText)
