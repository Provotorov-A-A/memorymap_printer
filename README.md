# Memory Layout Printer
Package provides some basic tools for creating memory map from memory blocks and printing it as a text.
Package can be used for visual comparing of memory maps (e.g. in embedded systems ).

# Result examples

Example 1
```
+------------------------------+------------------------------+
|       0x0, size = 0x10       |       0x0, size = 0x10       |
+------------------------------+------------------------------+
|         DR1(0x0-0xF)         |         DR1(0x0-0xF)         |
+------------------------------+------------------------------+
```
Example 2
```
+------------------------------+------------------------------+
|       0x0, size = 0x20       |       0x0, size = 0x10       |
+------------------------------+------------------------------+
|        DR1(0x00-0x0F)        |        DR1(0x00-0x0F)        |
+------------------------------+------------------------------+
| XXXXXXXXXXXXXXXXXXXXXXXXXXXX |                               
+------------------------------+                               
```
Example 3
```
+------------------------------+------------------------------+
|      0x15, size = 0x68       |      0x0, size = 0x100       |
+------------------------------+------------------------------+
                               | XXXXXXXXXXXXXXXXXXXXXXXXXXXX |
                               +------------------------------+
                               |        DR0(0x08-0x0F)        |
                               +------------------------------+
                               |        DR1(0x10-0x1F)        |
+------------------------------+                              |
|         (0x15-0x24)          |                              |
|                              |------------------------------+
|                              | XXXXXXXXXXXXXXXXXXXXXXXXXXXX |
+------------------------------+ XXXXXXXXXXXXXXXXXXXXXXXXXXXX |
| XXXXXXXXXXXXXXXXXXXXXXXXXXXX | XXXXXXXXXXXXXXXXXXXXXXXXXXXX |
+------------------------------+------------------------------+
|         (0x30-0x4F)          |      STATUS(0x30-0x4F)       |
+------------------------------+------------------------------+
| XXXXXXXXXXXXXXXXXXXXXXXXXXXX |       CNTRL(0x50-0x5F)       |
| XXXXXXXXXXXXXXXXXXXXXXXXXXXX |------------------------------+
| XXXXXXXXXXXXXXXXXXXXXXXXXXXX | XXXXXXXXXXXXXXXXXXXXXXXXXXXX |
+------------------------------+------------------------------+
|         (0x70-0x77)          |     Reserved0(0x70-0x7F)     |
+------------------------------+                              |
| XXXXXXXXXXXXXXXXXXXXXXXXXXXX |                              |
+------------------------------+------------------------------+
                               |     Reserved1(0x80-0x8F)     |
                               +------------------------------+
                               | XXXXXXXXXXXXXXXXXXXXXXXXXXXX |
                               +------------------------------+
```
Example 4
```
+------------------------------+------------------------------+------------------------------+
|      0x10, size = 0x20       |      0x10, size = 0x20       |       0x0, size = 0x20       |
+------------------------------+------------------------------+------------------------------+
                                                              |        DR1(0x00-0x0F)        |
+------------------------------+------------------------------+------------------------------+
|        DR1(0x10-0x1F)        |        DR1(0x10-0x1F)        | XXXXXXXXXXXXXXXXXXXXXXXXXXXX |
+------------------------------+------------------------------+------------------------------+
| XXXXXXXXXXXXXXXXXXXXXXXXXXXX | XXXXXXXXXXXXXXXXXXXXXXXXXXXX |                               
+------------------------------+------------------------------+       
```
Example 5
```
+------------------------------+------------------------------+
|       0x0, size = 0x8        |       0x0, size = 0x8        |
+------------------------------+------------------------------+
|           Bit0[0]            |            A0[0]             |
+------------------------------+------------------------------+
|           Bit1[1]            |           A1[2:1]            |
+------------------------------+                              |
|        BitField2[3:2]        |                              |
|                              |------------------------------+
|                              |            A2[3]             |
+------------------------------+------------------------------+
|        BitField3[5:4]        |           A3[5:4]            |
+------------------------------+------------------------------+
| XXXXXXXXXXXXXXXXXXXXXXXXXXXX |            A4[6]             |
+------------------------------+------------------------------+
|           Bit4[7]            | XXXXXXXXXXXXXXXXXXXXXXXXXXXX |
+------------------------------+------------------------------+
```

## How to use
```
from memorymap_printer import MemoryBlock, MemoryLayout, LayoutComparatorConfig, MemoryLayoutPrinter

m00 = MemoryBlock(0x00, 0x12, 'DR1')
ml0 = MemoryLayout(begin_address=0x00, size=0x20)
ml0.append_mem_block(m00)
ml0.fill_gaps()

m10 = MemoryBlock(0x00, 0x10, 'DR1')
ml1 = MemoryLayout(begin_address=0x00, size=0x10)
ml1.append_mem_block(m10)
ml1.fill_gaps()

lp = MemoryLayoutPrinter(LayoutComparatorConfig())
lp.add_layout(ml0, f'Reference layout (0x{ml0.begin_address():0X}-0x{ml0.end_address():0X})')
lp.add_layout(ml1, f'Comp layout (0x{ml1.begin_address():0X}-0x{ml1.end_address():0X})')

table_data = lp.to_text()
print(table_data)
```

## License
THIS PACKET IS PROVIDED "AS IS, WHERE IS, AND WITH NO
WARRANTY OF ANY KIND EITHER EXPRESSED OR IMPLIED, INCLUDING
BUT NOT LIMITED TO ANY IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS FOR A PARTICULAR PURPOSE."

