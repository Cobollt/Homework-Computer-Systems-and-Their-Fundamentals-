org 0x100

section .data
    a db 5
    b db 3
    c db 2
    resultMsg db 'Result: $'

section .text
_start:
    mov al, [b]
    sub al, [c]
    add al, [a]

    add al, 30h
    mov bl, al

    mov ah, 09h
    lea dx, resultMsg
    int 21h

    mov dl, bl
    mov ah, 02h
    int 21h

    mov ax, 4c00h
    int 21h