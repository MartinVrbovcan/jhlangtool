import sys
from . import processArgs
import pkg_resources
from . import FromJsonToExcel
from . import FromExcelToJson

def main():
    version = "0.8.0"
    try:
        for e in sys.argv[1:]:
            e = e.lower()
            if e == "generateexcel" or e == "toexcel":
                FromJsonToExcel.fromJsonToExcel(*processArgs.processJsonToExcelArgs(sys.argv[2:]))
                quit()
            elif e == "generatejson" or e == "tojson":
                FromExcelToJson.fromExcelToJson(*processArgs.processExcelToJsonArgs(sys.argv[2:]))
                quit()
    except TypeError:
        quit()
    if "-h" in sys.argv[1:] or "--help" in sys.argv[1:]:
        print(pkg_resources.resource_string(__name__, "helpMessages/toolHelp.txt").decode())
        quit()
    elif "-v" in sys.argv[1:] or "--version" in sys.argv[1:]:
        print(version)
    else:
        print("No keyword specified")
        print(pkg_resources.resource_string(__name__, "helpMessages/toolHelp.txt").decode())
        quit()

if __name__ == "__main__":
    main()