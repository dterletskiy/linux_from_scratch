lexer grammar XdlLexer;

import FragmentsLexer ;



DEF_VERSION                   : 'version'          F_COLON -> pushMode( MODE_VERSION );
DEF_AUTHOR                    : 'author'           F_COLON ;
DEF_DATA                      : 'data'             F_COLON ;
DEF_STRUCT                    : 'struct'           F_COLON ;
DEF_FIELD                     : 'field'            F_COLON ;
DEF_FUNCTION                  : 'function'         F_COLON ;
DEF_METHOD                    : 'method'           F_COLON ;
DEF_INTERFACE                 : 'interface'        F_COLON ;
DEF_REQUEST                   : 'request'          F_COLON ;
DEF_RESPONSE                  : 'response'         F_COLON ;
DEF_ATTRIBUTE                 : 'attribute'        F_COLON ;
DEF_IPC                       : 'ipc'              F_COLON ;
DEF_COMPONENT                 : 'component'        F_COLON ;
DEF_COMPONENTS                : 'components'       F_COLON ;
DEF_INCLUDE                   : 'include'          F_COLON -> pushMode( MODE_INCLUDE ) ;
DEF_IMPORT                    : 'import'           F_COLON -> pushMode( MODE_IMPORT ) ;
DEF_ROOT_DIR                  : 'root_dir'         F_COLON -> pushMode( MODE_PATH ) ;
DEF_CREATOR                   : 'creator'          F_COLON ;
DEF_THREAD                    : 'thread'           F_COLON ;
DEF_THREADS                   : 'threads'          F_COLON ;
DEF_WATCHDOG                  : 'watchdog'         F_COLON ;
DEF_APPLICATION               : 'application'      F_COLON ;
DEF_PROJECT                   : 'project'          F_COLON ;
DEF_DEFCONFIG                 : 'defconfig'        F_COLON ;
DEF_TYPE                      : 'type'             F_COLON ;
DEF_ARCH                      : 'arch'             F_COLON ;
DEF_LUNCH                     : 'lunch'            F_COLON ;
DEF_VARIANT                   : 'variant'          F_COLON ;
DEF_PRODUCT_NAME              : 'product_name'     F_COLON ;
DEF_PRODUCT_DEVICE            : 'product_device'   F_COLON ;

TRUE                          : 'true' ;
FALSE                         : 'false' ;

LEFT_ROUND_BRACKET            : F_LEFT_ROUND_BRACKET ;
RIGHT_ROUND_BRACKET           : F_RIGHT_ROUND_BRACKET ;
LEFT_SQUARE_BRACKET           : F_LEFT_SQUARE_BRACKET ;
RIGHT_SQUARE_BRACKET          : F_RIGHT_SQUARE_BRACKET ;
LEFT_CURLY_BRACKET            : F_LEFT_CURLY_BRACKET ;
RIGHT_CURLY_BRACKET           : F_RIGHT_CURLY_BRACKET ;
DOT                           : F_DOT ;
COMMA                         : F_COMMA ;
SEMICOLON                     : F_SEMICOLON ;
COLON                         : F_COLON ;
QUOTES                        : F_QUOTES ;
APOSTROPHE                    : F_APOSTROPHE ;
BACK_APOSTROPHE               : F_BACK_APOSTROPHE ;
ASTERISK                      : F_ASTERISK ;
SLASH                         : F_SLASH ;
BACK_SLASH                    : F_BACK_SLASH ;
PIPE                          : F_PIPE ;
PLUS                          : F_PLUS ;
MINUS                         : F_MINUS ;
UNDERSCORE                    : F_UNDERSCORE ;
EQUAL                         : F_EQUAL ;
LESS                          : F_LESS ;
GREATER                       : F_GREATER ;
AMPERSAND                     : F_AMPERSAND ;

SELECTOR                      : F_SELECTOR ;

WHITESPACE                    : (' ' | '\t')+ -> skip ;
NEWLINE                       : ('\r'? '\n' | '\r')+ -> skip ;

NUMBER                        : F_DIGIT+ ;

COMMENT                       : (F_BLOCK_COMMENT | F_LINE_COMMENT) -> channel(HIDDEN) ;

IDENTIFIER                    : (F_LETTER | F_UNDERSCORE) (F_LETTER | F_DIGIT | F_UNDERSCORE | F_MINUS)* ;

// NAMESPACE_NAME                : '::'? (IDENTIFIER '::')* IDENTIFIER ;
NAMESPACE                     : '::'? (IDENTIFIER '::')+ ;



/***************************************************************************
 *
 * MODE "PATH"
 *
 ***************************************************************************/

mode MODE_PATH;

MODE_PATH_PATH                : (F_LETTER | F_DIGIT | F_UNDERSCORE | F_DOT | F_SLASH)+ ;
MODE_PATH_WHITESPACE          : (' ' | '\t')+ -> skip ;
MODE_PATH_NEWLINE             : ('\r'? '\n' | '\r')+ -> skip ;
MODE_PATH_QUOTES              : F_QUOTES ;
MODE_PATH_COLON               : F_COLON ;
MODE_PATH_SEMICOLON           : F_SEMICOLON -> popMode ;



/***************************************************************************
 *
 * MODE "INCLUDE"
 *
 ***************************************************************************/

mode MODE_INCLUDE;

MODE_INCLUDE_PATH             : (F_LETTER | F_DIGIT | F_UNDERSCORE | F_DOT | F_SLASH)+ ;
MODE_INCLUDE_WHITESPACE       : (' ' | '\t')+ -> skip ;
MODE_INCLUDE_NEWLINE          : ('\r'? '\n' | '\r')+ -> skip ;
MODE_INCLUDE_QUOTES           : F_QUOTES ;
MODE_INCLUDE_COLON            : F_COLON ;
MODE_INCLUDE_SEMICOLON        : F_SEMICOLON -> popMode ;



/***************************************************************************
 *
 * MODE "IMPORT"
 *
 ***************************************************************************/

mode MODE_IMPORT;

MODE_IMPORT_PATH              : (F_LETTER | F_DIGIT | F_UNDERSCORE | F_DOT | F_SLASH)+ ;
MODE_IMPORT_WHITESPACE        : (' ' | '\t')+ -> skip ;
MODE_IMPORT_NEWLINE           : ('\r'? '\n' | '\r')+ -> skip ;
MODE_IMPORT_QUOTES            : F_QUOTES ;
MODE_IMPORT_COLON             : F_COLON ;
MODE_IMPORT_SEMICOLON         : F_SEMICOLON -> popMode ;



/***************************************************************************
 *
 * MODE "VERSION"
 *
 ***************************************************************************/

mode MODE_VERSION;

MODE_VERSION_NUMBER           : F_DIGIT+ F_DOT F_DIGIT+ F_DOT F_DIGIT+ ;
MODE_VERSION_NUMBER_EXT       : (F_LETTER | F_DIGIT) (F_LETTER | F_DIGIT | F_UNDERSCORE | F_MINUS | F_DOT)* ;
MODE_VERSION_WHITESPACE       : (' ' | '\t')+ -> skip ;
MODE_VERSION_NEWLINE          : ('\r'? '\n' | '\r')+ -> popMode ;
MODE_VERSION_SEMICOLON        : F_SEMICOLON -> popMode ;






/***************************************************************************
 *
 * DEC_DIGIT                     : F_DEC_DIGIT ;
 * HEX_DIGIT                     : F_HEX_DIGIT ;
 * OCT_DIGIT                     : F_OCT_DIGIT ;
 * BIN_DIGIT                     : F_BIN_DIGIT ;
 *
 * DEC_INT                : F_DEC_DIGIT+ ;
 * DEC_FLOAT              : F_DEC_DIGIT+ [.,] F_DEC_DIGIT+ ;
 *
 * HEX_INT                : '0' [Xx] F_HEX_DIGIT+ ;
 *
 * OCT_INT                : '0' F_OCT_DIGIT+ ;
 *
 * BIN_INT                : F_BIN_DIGIT+ 'b' ;
 *
 ***************************************************************************/

/***************************************************************************
 *
 * Nested curly braces
 * http://web.mit.edu/dmaze/school/6.824/antlr-2.7.0/doc/lexer.html
 *
 * SCOPE                         : '{' ( SCOPE | ~'}' )* '}' ;
 ***************************************************************************/
