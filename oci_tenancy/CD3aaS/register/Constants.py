class Constants:
    ID_TOKEN_CLOCK_SKEW = "IdTokenClockSkew"
    ID_TOKEN_CLOCK_SKEW_DEFAULT = 300
    ID_TOKEN_CLAIM_ISSUER = "IdTokenClaimIssuer"
    ID_TOKEN_CLAIM_APPROLES = "AppRolesTokenClaim"
    ID_TOKEN_CLAIM_APPROLES_DEFAULT = "appRoles"
    ID_TOKEN_CLAIM_GROUPS = "GroupsTokenClaim"
    ID_TOKEN_CLAIM_GROUPS_DEFAULT = "groups"
    ID_TOKEN_CLAIM_USERNAME = "UserNameTokenClaim"
    ID_TOKEN_CLAIM_USERNAME_DEFAULT = "sub"
    ID_TOKEN_CLAIM_DISPLAYNAME_DEFAULT = "user_displayname"
    ID_TOKEN_CLAIM_USERID = "UserIDTokenClaim"
    ID_TOKEN_CLAIM_USERID_DEFAULT = "user_id"
    ID_TOKEN_CLAIM_TENANT = "TenantTokenClaim"
    ID_TOKEN_CLAIM_TENANT_DEFAULT = "user_tenantname"
    ID_TOKEN_HEADER_KEY = "idcs_user_assertion"
    TOKEN_CLAIM_JTI = "jti"
    TOKEN_TYPE_JWT = "JWT"
    HEADER_CLAIM_TYPE = "typ"
    HEADER_CLAIM_KEY_ID = "kid"
    HEADER_CLAIM_X5_THUMB = "x5t"
    TOKEN_CLAIM_EXPIRY = "exp"
    TOKEN_CLAIM_AUDIENCE = "aud"
    TOKEN_CLAIM_ISSUE_AT = "iat"
    TOKEN_CLAIM_ISSUER = "iss"
    TOKEN_CLAIM_SCOPE = "scope"
    TOKEN_CLAIM_TENANT = "tenant"
    TOKEN_CLAIM_USER_APPROLES = "userAppRoles"
    TOKEN_CLAIM_CLIENT_APPROLES = "clientAppRoles"
    TOKEN_CLAIM_SUBJECT = "sub"
    TOKEN_CLAIM_TOKEN_TYPE = "tok_type"
    TOKEN_CLAIM_CLIENT_ID = "client_id"
    TOKEN_CLAIM_USER_ID = "user_id"
    TOKEN_CLAIM_CLIENT_TENANT = "client_tenantname"
    TOKEN_CLAIM_USER_TENANT = "user_tenantname"
    TOKEN_CLAIM_GROUPS = "groups"
    TOKEN_CLAIM_APP_ROLES = "appRoles"
    TOKEN_CLAIM_CLIENT_TENANT_NAME = "client_tenantname"
    TENANT_HEADER_KEY = "x_resource_identity_domain_name"
    HOST = "Host"
    PORT = "Port"
    PROTOCOL = "Protocol"
    BASE_URL = "BaseUrl"
    MY_SCOPES = "urn:opc:idm:__myscopes__"
    DISCOVERY_PATH = "/.well-known/idcs-configuration"
    GET_USER_PATH = "/admin/v1/Users/%s"
    GET_GROUP_MEMBERSHIP_PATH = "/admin/v1/Users/%s?attributes=groups"
    GET_ME_PATH = "/admin/v1/Me"
    GET_APP_INFO_PATH = "/admin/v1/Apps"
    FQS_FILTER = "scopes.fqs eq \"%s\""
    CLIENT_ID = "ClientId"
    CLIENT_SECRET = "ClientSecret"
    CLIENT_TENANT = "ClientTenant"
    AUDIENCE_SERVICE_URL = "AudienceServiceUrl"
    RESOURCE_TENANCY = "ResourceTenancy"
    CROSS_TENANT = "CrossTenant"
    TOKEN_ISSUER = "TokenIssuer"
    TOKEN_CLOCK_SKEW = "TokenClockSkew"
    IGNORE_SSL = "ignoreSSL"
    APP_NAME = "AppName"
    USER_ID_RES_ATTR = "UserIDResourceAttribute"
    CLIENT_ID_TOK_CLAIM = "ClientIDTokenClaim"
    USER_ID_TOK_CLAIM = "UserIDTokenClaim"
    CLIENT_TENANT_TOK_CLAIM = "ClientTenantTokenClaim"
    TOKEN_CLAIM_SUB_TYPE= "sub_type"
    USER_TENANT_TOKEN_CLAIM = "TenantTokenClaim"
    ONLY_USER_TOK_CLAIM_ENABLED = "OnlyUserTokenClaimsEnabled"
    GROUP_TOKEN_CLAIM = "GroupsTokenClaim"
    APP_ROLE_TOKEN_CLAIM = "AppRolesTokenClaim"
    TOKEN_VALIDATION_LEVEL = "TokenValidationLevel"
    FULLY_QUALIFIED_SCOPES = "FullyQualifiedScopes"
    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"
    ID_TOKEN = "id_token"
    ASSERTER_CACHE = "asserter_cache"
    USER_CACHE = "user_cache"
    FQS_CACHE = "fqs_cache"
    TOKEN_CACHE = "token_cache"
    USER_CACHE_TTL = "UserCacheTTL"
    USER_CACHE_TTL_DEFAULT = 86400
    USER_CACHE_MAX_SIZE = "UserCacheMaxSize"
    USER_CACHE_MAX_SIZE_DEFAULT = 10000
    META_DATA_CACHE_TTL = "MetaDataCacheTTL"
    META_DATA_CACHE_TTL_DEFAULT = 86400
    META_DATA_CACHE_MAX_SIZE = "MetaDataCacheMaxSize"
    META_DATA_CACHE_MAX_SIZE_DEFAULT = 1000
    FQS_RESOURCE_CACHE_TTL = "FQSResourceTTL"
    FQS_RESOURCE_CACHE_TTL_DEFAULT = 600
    CACHE_TTL_DEFAULT= 86400
    CACHE_MAX_SIZE_DEFAULT= 10000
    META_OPENID_CONFIGURATION = "openid-configuration"
    META_OPENID_CONFIGURATION_ISSUER = "issuer"
    META_OPENID_CONFIGURATION_TOKEN_ENDPOINT = "token_endpoint"
    META_OPENID_CONFIGURATION_AUTHORIZATION_ENDPOINT = "authorization_endpoint"
    META_ACCESS_CONFIGURATION = "access-configuration"
    META_ACCESS_CONFIGURATION_ASSERTER_ENDPOINT = "asserter_endpoint"
    META_OPENID_CONFIGURATION_ENDSESSION_ENDPOINT = 'end_session_endpoint'
    META_JWKS_URI = "jwks_uri"
    LOG_LEVEL = "LogLevel"
    CONSOLE_LOG = "ConsoleLog"
    KEYS = "keys"
    X5C = "x5c"
    ALG = "alg"
    UTF8 = 'utf-8'
    HEADER_AUTHORIZATION = "Authorization"
    HEADER_CONTENT = "Content-type"
    APPLICATION_JSON = "application/json"
    PARAM_USER_NAME = "username"
    PARAM_PASSWORD = "password"
    PARAM_CLIENT_ID = "client_id"
    PARAM_RESPONSE_TYPE = "response_type"
    PARAM_REDIRECT_URI = "redirect_uri"
    PARAM_NONCE = "nonce"
    PARAM_ASSERTION = "assertion"
    PARAM_CLIENT_ASSERTION = "client_assertion"
    PARAM_CLIENT_ASSERTION_TYPE = "client_assertion_type"
    PARAM_SCOPE = "scope"
    PARAM_STATE = "state"
    PARAM_GRANT_TYPE = "grant_type"
    PARAM_CODE = "code"
    PARAM_REFRESH_TOKEN = "refresh_token"
    PARAM_ATTRIBUTES = "attributes"
    PARAM_POST_LOGOUT_URI = "post_logout_redirect_uri"
    PARAM_ID_TOKEN_HINT = "id_token_hint"
    USER_ATTRIBUTES = "username,displayname,emails,groups,urn:ietf:params:scim:schemas:oracle:idcs:extension:user:User:appRoles"
    IDCS_ASSERTER_SCHEMA = "urn:ietf:params:scim:schemas:oracle:idcs:Asserter"
    IDCS_APPNAME_FILTER_ATTRIB = "appName"
    IDCS_MAPPING_ATTRIBUTE = "mappingAttribute"
    IDCS_MAPPING_ATTRIBUTE_VALUE = "mappingAttributeValue"
    SUBJECT_TYPE_ATTR = "subjectType"
    MAPPING_ATTR_ID = "id"
    IDCS_SCHEMAS = "schemas"
    IDCS_INCLUDE_MEMBERSHIPS = "includeMemberships"
    AUTH_BASIC = "Basic %s"
    AUTH_BEARER = "Bearer %s"
    RESPONSE_TYPE_CODE = "code"
    GRANT_CLIENT_CRED = "client_credentials"
    GRANT_AUTHZ_CODE = "authorization_code"
    GRANT_PASSWORD = "password"
    GRANT_REFRESH_TOKEN = "refresh_token"
    GRANT_ASSERTION = "urn:ietf:params:oauth:grant-type:jwt-bearer"
    ASSERTION_JWT = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
    WWW_FORM_ENCODED = "application/x-www-form-urlencoded"
    CLAIM_USER_NAME = "userName"
    CLAIM_DISPLAY_NAME = "displayName"
    CLAIM_ID = "id"
    CLAIM_IDENTITY_DOMAIN = "identityDomain"
    CLAIM_ID_TOKEN = "_idToken"
    CLAIM_ACTIVE = "active"
    CLAIM_META = "meta"
    CLAIM_USER_EXTENSIONS = "urn:ietf:params:scim:schemas:oracle:idcs:extension:user:User"
    CLAIM_GROUPS = "groups"
    CLAIM_APP_ROLES = "appRoles"
    CLAIM_GROUP_DISPLAY_NAME = "display"
    CLAIM_GROUP_ID = "value"
    CLAIM_GROUP_LOCATION = "$ref"
    CLAIM_APP_ROLE_DISPLAY = "display"
    CLAIM_APP_ROLE_APPNAME = "appName"
    CLAIM_APP_ROLE_ADMIN = "adminRole"
    CLAIM_APP_ROLE_APPID = "appId"
    CLAIM_APP_ROLE_VALUE = "value"
    CLAIM_APP_ROLE_LOCATION = "$ref"
    ORA_IDCS_BASE_URL = "ORA_IDCS_BASE_URL"
    ORA_IDCS_CLIENT_ID = "ORA_IDCS_CLIENT_ID"
    ORA_IDCS_CLIENT_SECRET = "ORA_IDCS_CLIENT_SECRET"
    ORA_IDCS_AUDIENCE_URL = "ORA_IDCS_AUDIENCE_URL"
    ORA_IDCS_ISSUER_URL = "ORA_IDCS_ISSUER_URL"
    ORA_IDCS_CROSS_TENANT = "ORA_IDCS_CROSS_TENANT"
    ORA_IDCS_RESOURCE_TENANCY = "ORA_IDCS_RESOURCE_TENANCY"
    ORA_IDCS_TOKEN_VALIDATION_LEVEL = "ORA_IDCS_TOKEN_VALIDATION_LEVEL"
    ORA_IDCS_FQS_RESOURCE = "ORA_IDCS_FQS_RESOURCE"
    VALIDATION_LEVEL_NONE= "NONE"
    VALIDATION_LEVEL_SIGNATURE= "SIGNATURE"
    VALIDATION_LEVEL_NORMAL= "NORMAL"
    VALIDATION_LEVEL_FULL= "FULL"
    NECESSARY_AUDIENCE_PREFIX = "urn:opc:resource:scope:"
    LOGICALGUID_AUDIENCE_PREFIX = "urn:opc:lbaas:logicalguid"
    AUDIENCE_SCOPE_ACCOUNT = "urn:opc:resource:scope:account"
    AUDIENCE_SCOPE_TAG = "urn:opc:resource:scope:tag"
    TOKEN_CLOCK_SKEW_DEFAULT_VALUE = 120
    HASH = "hash"
class Constants:
    ID_TOKEN_CLOCK_SKEW = "IdTokenClockSkew"
    ID_TOKEN_CLOCK_SKEW_DEFAULT = 300
    ID_TOKEN_CLAIM_ISSUER = "IdTokenClaimIssuer"
    ID_TOKEN_CLAIM_APPROLES = "AppRolesTokenClaim"
    ID_TOKEN_CLAIM_APPROLES_DEFAULT = "appRoles"
    ID_TOKEN_CLAIM_GROUPS = "GroupsTokenClaim"
    ID_TOKEN_CLAIM_GROUPS_DEFAULT = "groups"
    ID_TOKEN_CLAIM_USERNAME = "UserNameTokenClaim"
    ID_TOKEN_CLAIM_USERNAME_DEFAULT = "sub"
    ID_TOKEN_CLAIM_DISPLAYNAME_DEFAULT = "user_displayname"
    ID_TOKEN_CLAIM_USERID = "UserIDTokenClaim"
    ID_TOKEN_CLAIM_USERID_DEFAULT = "user_id"
    ID_TOKEN_CLAIM_TENANT = "TenantTokenClaim"
    ID_TOKEN_CLAIM_TENANT_DEFAULT = "user_tenantname"
    ID_TOKEN_HEADER_KEY = "idcs_user_assertion"
    TOKEN_CLAIM_JTI = "jti"
    TOKEN_TYPE_JWT = "JWT"
    HEADER_CLAIM_TYPE = "typ"
    HEADER_CLAIM_KEY_ID = "kid"
    HEADER_CLAIM_X5_THUMB = "x5t"
    TOKEN_CLAIM_EXPIRY = "exp"
    TOKEN_CLAIM_AUDIENCE = "aud"
    TOKEN_CLAIM_ISSUE_AT = "iat"
    TOKEN_CLAIM_ISSUER = "iss"
    TOKEN_CLAIM_SCOPE = "scope"
    TOKEN_CLAIM_TENANT = "tenant"
    TOKEN_CLAIM_USER_APPROLES = "userAppRoles"
    TOKEN_CLAIM_CLIENT_APPROLES = "clientAppRoles"
    TOKEN_CLAIM_SUBJECT = "sub"
    TOKEN_CLAIM_TOKEN_TYPE = "tok_type"
    TOKEN_CLAIM_CLIENT_ID = "client_id"
    TOKEN_CLAIM_USER_ID = "user_id"
    TOKEN_CLAIM_CLIENT_TENANT = "client_tenantname"
    TOKEN_CLAIM_USER_TENANT = "user_tenantname"
    TOKEN_CLAIM_GROUPS = "groups"
    TOKEN_CLAIM_APP_ROLES = "appRoles"
    TOKEN_CLAIM_CLIENT_TENANT_NAME = "client_tenantname"
    TENANT_HEADER_KEY = "x_resource_identity_domain_name"
    HOST = "Host"
    PORT = "Port"
    PROTOCOL = "Protocol"
    BASE_URL = "BaseUrl"
    MY_SCOPES = "urn:opc:idm:__myscopes__"
    DISCOVERY_PATH = "/.well-known/idcs-configuration"
    GET_USER_PATH = "/admin/v1/Users/%s"
    GET_GROUP_MEMBERSHIP_PATH = "/admin/v1/Users/%s?attributes=groups"
    GET_ME_PATH = "/admin/v1/Me"
    GET_APP_INFO_PATH = "/admin/v1/Apps"
    FQS_FILTER = "scopes.fqs eq \"%s\""
    CLIENT_ID = "ClientId"
    CLIENT_SECRET = "ClientSecret"
    CLIENT_TENANT = "ClientTenant"
    AUDIENCE_SERVICE_URL = "AudienceServiceUrl"
    RESOURCE_TENANCY = "ResourceTenancy"
    CROSS_TENANT = "CrossTenant"
    TOKEN_ISSUER = "TokenIssuer"
    TOKEN_CLOCK_SKEW = "TokenClockSkew"
    IGNORE_SSL = "ignoreSSL"
    APP_NAME = "AppName"
    USER_ID_RES_ATTR = "UserIDResourceAttribute"
    CLIENT_ID_TOK_CLAIM = "ClientIDTokenClaim"
    USER_ID_TOK_CLAIM = "UserIDTokenClaim"
    CLIENT_TENANT_TOK_CLAIM = "ClientTenantTokenClaim"
    TOKEN_CLAIM_SUB_TYPE= "sub_type"
    USER_TENANT_TOKEN_CLAIM = "TenantTokenClaim"
    ONLY_USER_TOK_CLAIM_ENABLED = "OnlyUserTokenClaimsEnabled"
    GROUP_TOKEN_CLAIM = "GroupsTokenClaim"
    APP_ROLE_TOKEN_CLAIM = "AppRolesTokenClaim"
    TOKEN_VALIDATION_LEVEL = "TokenValidationLevel"
    FULLY_QUALIFIED_SCOPES = "FullyQualifiedScopes"
    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"
    ID_TOKEN = "id_token"
    ASSERTER_CACHE = "asserter_cache"
    USER_CACHE = "user_cache"
    FQS_CACHE = "fqs_cache"
    TOKEN_CACHE = "token_cache"
    USER_CACHE_TTL = "UserCacheTTL"
    USER_CACHE_TTL_DEFAULT = 86400
    USER_CACHE_MAX_SIZE = "UserCacheMaxSize"
    USER_CACHE_MAX_SIZE_DEFAULT = 10000
    META_DATA_CACHE_TTL = "MetaDataCacheTTL"
    META_DATA_CACHE_TTL_DEFAULT = 86400
    META_DATA_CACHE_MAX_SIZE = "MetaDataCacheMaxSize"
    META_DATA_CACHE_MAX_SIZE_DEFAULT = 1000
    FQS_RESOURCE_CACHE_TTL = "FQSResourceTTL"
    FQS_RESOURCE_CACHE_TTL_DEFAULT = 600
    CACHE_TTL_DEFAULT= 86400
    CACHE_MAX_SIZE_DEFAULT= 10000
    META_OPENID_CONFIGURATION = "openid-configuration"
    META_OPENID_CONFIGURATION_ISSUER = "issuer"
    META_OPENID_CONFIGURATION_TOKEN_ENDPOINT = "token_endpoint"
    META_OPENID_CONFIGURATION_AUTHORIZATION_ENDPOINT = "authorization_endpoint"
    META_ACCESS_CONFIGURATION = "access-configuration"
    META_ACCESS_CONFIGURATION_ASSERTER_ENDPOINT = "asserter_endpoint"
    META_OPENID_CONFIGURATION_ENDSESSION_ENDPOINT = 'end_session_endpoint'
    META_JWKS_URI = "jwks_uri"
    LOG_LEVEL = "LogLevel"
    CONSOLE_LOG = "ConsoleLog"
    KEYS = "keys"
    X5C = "x5c"
    ALG = "alg"
    UTF8 = 'utf-8'
    HEADER_AUTHORIZATION = "Authorization"
    HEADER_CONTENT = "Content-type"
    APPLICATION_JSON = "application/json"
    PARAM_USER_NAME = "username"
    PARAM_PASSWORD = "password"
    PARAM_CLIENT_ID = "client_id"
    PARAM_RESPONSE_TYPE = "response_type"
    PARAM_REDIRECT_URI = "redirect_uri"
    PARAM_NONCE = "nonce"
    PARAM_ASSERTION = "assertion"
    PARAM_CLIENT_ASSERTION = "client_assertion"
    PARAM_CLIENT_ASSERTION_TYPE = "client_assertion_type"
    PARAM_SCOPE = "scope"
    PARAM_STATE = "state"
    PARAM_GRANT_TYPE = "grant_type"
    PARAM_CODE = "code"
    PARAM_REFRESH_TOKEN = "refresh_token"
    PARAM_ATTRIBUTES = "attributes"
    PARAM_POST_LOGOUT_URI = "post_logout_redirect_uri"
    PARAM_ID_TOKEN_HINT = "id_token_hint"
    USER_ATTRIBUTES = "username,displayname,emails,groups,urn:ietf:params:scim:schemas:oracle:idcs:extension:user:User:appRoles"
    IDCS_ASSERTER_SCHEMA = "urn:ietf:params:scim:schemas:oracle:idcs:Asserter"
    IDCS_APPNAME_FILTER_ATTRIB = "appName"
    IDCS_MAPPING_ATTRIBUTE = "mappingAttribute"
    IDCS_MAPPING_ATTRIBUTE_VALUE = "mappingAttributeValue"
    SUBJECT_TYPE_ATTR = "subjectType"
    MAPPING_ATTR_ID = "id"
    IDCS_SCHEMAS = "schemas"
    IDCS_INCLUDE_MEMBERSHIPS = "includeMemberships"
    AUTH_BASIC = "Basic %s"
    AUTH_BEARER = "Bearer %s"
    RESPONSE_TYPE_CODE = "code"
    GRANT_CLIENT_CRED = "client_credentials"
    GRANT_AUTHZ_CODE = "authorization_code"
    GRANT_PASSWORD = "password"
    GRANT_REFRESH_TOKEN = "refresh_token"
    GRANT_ASSERTION = "urn:ietf:params:oauth:grant-type:jwt-bearer"
    ASSERTION_JWT = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
    WWW_FORM_ENCODED = "application/x-www-form-urlencoded"
    CLAIM_USER_NAME = "userName"
    CLAIM_DISPLAY_NAME = "displayName"
    CLAIM_ID = "id"
    CLAIM_IDENTITY_DOMAIN = "identityDomain"
    CLAIM_ID_TOKEN = "_idToken"
    CLAIM_ACTIVE = "active"
    CLAIM_META = "meta"
    CLAIM_USER_EXTENSIONS = "urn:ietf:params:scim:schemas:oracle:idcs:extension:user:User"
    CLAIM_GROUPS = "groups"
    CLAIM_APP_ROLES = "appRoles"
    CLAIM_GROUP_DISPLAY_NAME = "display"
    CLAIM_GROUP_ID = "value"
    CLAIM_GROUP_LOCATION = "$ref"
    CLAIM_APP_ROLE_DISPLAY = "display"
    CLAIM_APP_ROLE_APPNAME = "appName"
    CLAIM_APP_ROLE_ADMIN = "adminRole"
    CLAIM_APP_ROLE_APPID = "appId"
    CLAIM_APP_ROLE_VALUE = "value"
    CLAIM_APP_ROLE_LOCATION = "$ref"
    ORA_IDCS_BASE_URL = "ORA_IDCS_BASE_URL"
    ORA_IDCS_CLIENT_ID = "ORA_IDCS_CLIENT_ID"
    ORA_IDCS_CLIENT_SECRET = "ORA_IDCS_CLIENT_SECRET"
    ORA_IDCS_AUDIENCE_URL = "ORA_IDCS_AUDIENCE_URL"
    ORA_IDCS_ISSUER_URL = "ORA_IDCS_ISSUER_URL"
    ORA_IDCS_CROSS_TENANT = "ORA_IDCS_CROSS_TENANT"
    ORA_IDCS_RESOURCE_TENANCY = "ORA_IDCS_RESOURCE_TENANCY"
    ORA_IDCS_TOKEN_VALIDATION_LEVEL = "ORA_IDCS_TOKEN_VALIDATION_LEVEL"
    ORA_IDCS_FQS_RESOURCE = "ORA_IDCS_FQS_RESOURCE"
    VALIDATION_LEVEL_NONE= "NONE"
    VALIDATION_LEVEL_SIGNATURE= "SIGNATURE"
    VALIDATION_LEVEL_NORMAL= "NORMAL"
    VALIDATION_LEVEL_FULL= "FULL"
    NECESSARY_AUDIENCE_PREFIX = "urn:opc:resource:scope:"
    LOGICALGUID_AUDIENCE_PREFIX = "urn:opc:lbaas:logicalguid"
    AUDIENCE_SCOPE_ACCOUNT = "urn:opc:resource:scope:account"
    AUDIENCE_SCOPE_TAG = "urn:opc:resource:scope:tag"
    TOKEN_CLOCK_SKEW_DEFAULT_VALUE = 120
    HASH = "hash"
