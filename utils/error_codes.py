class ErrorCodes:
    # Auth Errors (1xxx)
    INVALID_CREDENTIALS = "AUTH_001"
    TOKEN_EXPIRED = "AUTH_002"
    INVALID_TOKEN = "AUTH_003"
    USER_EXISTS = "AUTH_004"
    
    # Validation Errors (2xxx)
    INVALID_PHONE = "VAL_001"
    INVALID_CODE = "VAL_002"
    INVALID_INPUT = "VAL_003"
    
    # Permission Errors (3xxx)
    PERMISSION_DENIED = "PERM_001"
    NOT_PROVIDER = "PERM_002"
    
    # Resource Errors (4xxx)
    NOT_FOUND = "RES_001"
    ALREADY_EXISTS = "RES_002"