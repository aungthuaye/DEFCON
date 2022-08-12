p = list(map(lambda _: ord(_) - 0x21, "!!&!!dzăC|"))
i = "DÒVV×0Ë×YVR "

while p[2] < len(p):
    if (p[p[2]] & 0xC0) >> 6 == 0:
        p[p[p[2]] & 0x07] = (p[p[2]] & 0x38) >> 3
    elif (p[p[2]] & 0xC0) >> 6 == 1:
        if (p[p[2]] & 0x38) >> 3 == 0:
            p[0] = ((((ord(i[0]) - 0x20) & 128) >> 7) | ((ord(i[0]) - 0x20) << 1)) & 0xFF
            i = i[1:]
        p[p[p[2]] & 0x07] = p[(p[p[2]] & 0x38) >> 3]
        if p[p[2]] & 0x07 == 1:
            print(chr(p[1]), end="")
    elif (p[p[2]] & 0xC0) >> 6 == 2:
        p[p[p[2]] & 0x07] = (p[p[2]] & 0x38) >> 3 + p[p[p[2]] & 0x07]
    else:
        p[p[p[2]] & 0x07] = p[(p[p[2]] & 0x38) >> 3] + p[p[p[2]] & 0x07]
    p[2] += 1
    p[4] = 1 if p[3] == 0 else 0
