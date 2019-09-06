from enum import Enum


class ServiciosBSG(Enum):
    buscarPorNombreBSGRC = 'https://www.bsg.gob.ec/sw/RC/BSGSW02_Consultar_Nombre?wsdl'
    buscarPorCedulaRegCiv = 'https://www.bsg.gob.ec/sw/RC/BSGSW03_Consultar_Ciudadano?wsdl'
    bsgValidador = "https://www.bsg.gob.ec/sw/STI/BSGSW08_Acceder_BSG?wsdl"
    consultarTitulosBSGSENESCYT = "https://www.bsg.gob.ec/sw/SENESCYT/BSGSW04_Consultar_Titulos?wsdl"
    consultarDiscapacidadBSGMSP = "https://www.bsg.gob.ec/sw/MSP/BSGSW01_Consultar_Discapacidad?wsdl"


class SecurityHeader(Enum):
    wsseElement = "wsse"
    wsuElement = "wsu"
    wsse = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
    wsu = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"
    xmlnsWsu = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"
    username = "Username"
    securityElement = "Security"
    usernameToken = "UsernameToken"
    passwordElement = "Password"
    typeElement = "Type"
    passwordType = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest"
    nonceElement = "Nonce"
    encodingTypeElement = "EncodingType"
    encodingTypeNonce = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary"
    createdElement = "Created"
    timestampElement = "Timestamp"
    expiresTimestampElement = "Expires"
