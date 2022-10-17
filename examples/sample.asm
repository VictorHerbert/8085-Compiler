const1 equ (1+3)*2
const2 equ 3+const1

jmp start
jmp 1a54h

data0:  db const2
data1:  db const1
data1:  db const1

vector: ds 4
        db 2
        org 30
start:  mvi a, 4
        mvi a, const1+5
end:    mvi d, const2

; Lorem ipsum code

; I do not own the code bellow
; all credits goes to https://github.com/ashwek/8085

;8085 Program to multiply
;(BxD) 2 8-bit numbers

        MVI C, 00    ;Store 00 in C 

        LDA 5000     ;1st value, Load A from memory location 5000
        MOV B, A     ;copy content of A to B
        DCR B        ;Decrement B
        ORA A        ;Check is value in A (or B) is 0 or not
        JZ Exit      ;if Zero, jump to exit

        LDA 5001     ;2nd value, Load A from memory location 5001
        MOV D, A     ;copy content of A to D
        ORA A        ;Check if value of A (or D) is 0 or not

Loop:   JZ Exit      ;if Zero, jump to exit
        ADD D        ;Add D to A
        JNC NoCarry  ;if carry is not generated, jump to label NoCarry
        INR C        ;if carry is generated, increment C
NoCarry:DCR B        ;decrement B
        JMP Loop     ;Jump to label Loop

Exit:   STA 5003     ;store content of A (lower order of result) at memory location 5003
        MOV A, C     ;copy content of C to A
        STA 5002     ;store content of A(higher order of resut) at memory location 5002
        HLT          ;Halt program

;8085 Program to Divide
;(A/D) 2 8-bit numbers

     LDA 5001       ;Load value of divisor from address 5001 
     MOV D, A       ;move divisor from A to D

     LDA 5000       ;Load value of dividend from address 5000 

     MVI C, 0FFH    ;C is used to store the quotient, initial value is FF

Div: INR C          ;Increment quotient
     SUB D          ;Subtract D (divisor) from A (dividend)
     JNC Div        ;Jump if No Carry to label Div
     ADD D

     STA 5002       ;Store remainder at memory location 5002

     MOV A, C       ;copy content of C (quotient) into A
     STA 5003       ;Store quotient at location 5003

     HLT

;8085 Program to sort an
;array in ascending order

         LXI H, 5000   ;Starting address of array, stores array size
         MOV C, M      ;Store array size in C, used as Counter for OuterLoop
         DCR C         ;Decrement OutLoop counter

OutLoop: MOV D, C      ;Copy counter in D, used as InLoop counter

         LXI H, 5001   ;5001 stores 1st element of array

 InLoop: MOV A, M      ;store element of array in A
         INX H         ;goto next address
         CMP M         ;compare A (element) with next element

         JC Skip       ;if A < M, jump to skip
         MOV B, M      ;Swap elements
         MOV M, A
         DCX H
         MOV M, B
         INX H

   Skip: DCR D         ;Decrement InLoop counter
         JNZ InLoop    ;if D!=0 jump to InLoop

         DCR C         ;Decrement OutLoop counter
         JNZ OutLoop   ;if C!=0 jump to OutLoop

         HLT           ;HALT program

;8085 Program to sort an
;array in descending order

         LXI H, 5000   ;Starting address of array, stores array size
         MOV C, M      ;Store array size in C, used as Counter for OuterLoop
         DCR C         ;Decrement OutLoop counter

OutLoop: MOV D, C      ;Copy counter in D, used as InLoop counter

         LXI H, 5001   ;5001 stores 1st element of array

 InLoop: MOV A, M      ;store element of array in A
         INX H         ;goto next address
         CMP M         ;compare A (element) with next element

         JNC Skip       ;if A > M, jump to skip
         MOV B, M      ;Swap elements
         MOV M, A
         DCX H
         MOV M, B
         INX H

   Skip: DCR D         ;Decrement InLoop counter
         JNZ InLoop    ;if D!=0 jump to InLoop

         DCR C         ;Decrement OutLoop counter
         JNZ OutLoop   ;if C!=0 jump to OutLoop

         HLT           ;HALT program

;8085 Program to Divide
;(A/D) 2 8-bit numbers

     LDA 5001       ;Load value of divisor from address 5001 
     MOV D, A       ;move divisor from A to D

     LDA 5000       ;Load value of dividend from address 5000 

     MVI C, 0FFH    ;C is used to store the quotient, initial value is FF

Div: INR C          ;Increment quotient
     SUB D          ;Subtract D (divisor) from A (dividend)
     JNC Div        ;Jump if No Carry to label Div
     ADD D

     STA 5002       ;Store remainder at memory location 5002

     MOV A, C       ;copy content of C (quotient) into A
     STA 5003       ;Store quotient at location 5003

     HLT

;Program to check if a number at 5000 is Even
;or Odd. Store result at location 5001. 0 if Odd
;and 1 if Even


      MVI B, 01H   ;Load initial result as 1 (Even)

      LDA 5000     ;Load value from memory location 5000 into A

 Div: SBI 02H      ;Subtract 2 from A. A = A - 2
      JNC Div      ;if No Carry, jump to Div label
      ADI 02H      ;Add 2 to A. A = A + 2

      JZ Skip      ;if A = 0, jumo to Skip

      DCR B        ;if A != 0, Number is odd. decrement B

Skip: MOV A, B     ;copy result in A
      STA 5001     ;store result at memory location 5001

      HLT          ;HALT program