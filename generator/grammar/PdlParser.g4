parser grammar PdlParser;

import XdlParser;
options { tokenVocab=PdlLexer; }



content              : element+ EOF ;

element              : ( author | version | project ) ;

project              : DEF_PROJECT IDENTIFIER LEFT_CURLY_BRACKET ( type | root_dir | version | arch | defconfig | lunch | variant | product_name | product_device )* RIGHT_CURLY_BRACKET SEMICOLON ;
type                 : DEF_TYPE IDENTIFIER SEMICOLON ;
root_dir             : DEF_ROOT_DIR MODE_PATH_QUOTES MODE_PATH_PATH MODE_PATH_QUOTES MODE_PATH_SEMICOLON ;
arch                 : DEF_ARCH IDENTIFIER SEMICOLON ;
defconfig            : DEF_DEFCONFIG IDENTIFIER SEMICOLON ;
lunch                : DEF_LUNCH IDENTIFIER SEMICOLON ;
variant              : DEF_VARIANT IDENTIFIER SEMICOLON ;
product_name         : DEF_PRODUCT_NAME IDENTIFIER SEMICOLON ;
product_device       : DEF_PRODUCT_DEVICE IDENTIFIER SEMICOLON ;
