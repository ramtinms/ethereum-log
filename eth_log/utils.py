def split_by_len(seq, length):
    return [seq[i:i+length] for i in range(0, len(seq), length)]

def validate_address(string):
	if string.startswith('0x') and len(string) == 42:
		return string
	if not string.startswith('0x') and len(string) == 40:
		return '0x' + string
	return None
