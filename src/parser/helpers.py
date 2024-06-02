from lexer.tokens import TokenType

def get_precedence(token_type: TokenType) -> int:
    '''
    Returns the precedence of the given token type.
    
    Args:
        token_type (TokenType): The token type to get the precedence for.
        
    Returns:
        int: The precedence of the token type.
    '''
    precedence = {
        TokenType.LOGICAL_OR: 1,
        TokenType.LOGICAL_AND: 2,
        TokenType.EQUAL: 3,
        TokenType.NOT_EQUAL: 3,
        TokenType.LT: 4,
        TokenType.GT: 4,
        TokenType.LTE: 4,
        TokenType.GTE: 4,
        TokenType.PLUS: 5,
        TokenType.MINUS: 5,
        TokenType.MULTIPLY: 6,
        TokenType.DIVIDE: 6
    }
    
    return precedence.get(token_type, 0)