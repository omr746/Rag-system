from enum import Enum
class ResponseSignal(Enum):

    FILE_TYPE="file type not suppoted"
    FILE_SIZE="file size exceeded"
    FILE_UPLOADE_SUCCES="file uploaded succes"
    FILE_UPLOADE_FAILED="file uploaded falied"
    FILE_VALIDATED_SUCCES="file validate succes"