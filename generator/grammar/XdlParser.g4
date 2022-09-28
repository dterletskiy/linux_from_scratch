parser grammar XdlParser;

options { tokenVocab=XdlLexer; }



author               : DEF_AUTHOR IDENTIFIER (SEMICOLON | NEWLINE) ;

version              : DEF_VERSION (version_number | version_number_ext) (MODE_VERSION_SEMICOLON | MODE_VERSION_NEWLINE) ;
version_number       : MODE_VERSION_NUMBER ;
version_number_ext   : MODE_VERSION_NUMBER_EXT ;



procedure            : name arguments_list ;
function             : type name arguments_list ;
arguments_list       : LEFT_ROUND_BRACKET arguments? RIGHT_ROUND_BRACKET ;
arguments_tuple      : LEFT_SQUARE_BRACKET arguments? RIGHT_SQUARE_BRACKET ;
arguments            : argument ( COMMA argument )* ;
argument             : type name ;
type                 : NAMESPACE? ( IDENTIFIER | IDENTIFIER LESS IDENTIFIER GREATER ) AMPERSAND? ;
names                : name ( COMMA name )* ;
name                 : IDENTIFIER ;
