"""Some basic tools for creating memory map from memory blocks and printing it as a text.

Classes:
 - MemoryBlock - common class for memory block representing;
 - MemoryLayout - container class for memory blocks, has some handy method for layout manipulation;
 - MemoryLayoutPrinter - aimed to print text table for memory layouts comparing, can be used to print just one layout.

Example:
    m00 = MemoryBlock(0x00, 0x12, 'DR1')
    ml0 = MemoryLayout(begin_address=0x00, size=0x20)
    ml0.append_mem_block(m00)
    ml0.fill_gaps()

    m10 = MemoryBlock(0x00, 0x10, 'DR1')
    ml1 = MemoryLayout(begin_address=0x00, size=0x10)
    ml1.append_mem_block(m10)
    ml1.fill_gaps()

    lp = MemoryLayoutPrinter(MemoryLayoutPrinterConfig())
    lp.add_layout(ml0, f'Reference layout (0x{ml0.begin_address():0X}-0x{ml0.end_address():0X})')
    lp.add_layout(ml1, f'Comp layout (0x{ml1.begin_address():0X}-0x{ml1.end_address():0X})')

    table_data = lp.to_text()
    print(table_data)

@author Provotorov A. <merqcio11@gmail.com>
"""

import sys
from typing import List
from linked_list import *
from string_utils import max_strlen_in_list, hex_digits


class MemoryBlock:
    """Memory block with identifier.
    """
    def __init__(self, begin_address, size, identifier=None, unused=False):
        if size <= 0 or begin_address < 0:
            raise ValueError(f'Instance of {self.__class__} have negative start address or non-positive size!')
        self._begin_address = begin_address
        self._size = size
        self._end_address = self._begin_address + self._size - 1
        self._identifier = identifier
        self._unused = unused

    def __contains__(self, address):
        return self.begin_address() <= address <= self.end_address()

    def __eq__(self, other):
        """Instances are equal if they have equal begin address and size.
        """
        if other:
            return (self.begin_address() == other.begin_address()
                    and self.size() == other.size())
        else:
            return False

    def contains_region(self, mem_region):
        return mem_region.begin_address() >= self.begin_address() and mem_region.end_address() <= self.end_address()

    def begin_address(self):
        return self._begin_address

    def size(self):
        return self._size

    def end_address(self):
        return self._end_address

    def identifier(self):
        ret = '' if not self._identifier else self._identifier
        return ret

    def is_unused(self):
        return self._unused

    def __str__(self):
        return f'Instance of {self.__class__}: ' \
               f'{self.identifier()}(0x{self.begin_address():0X}-0x{self.end_address():0X})'


class MemoryLayoutError(Exception):
    """Memory block is not fit to specified address range.
    """
    def __init__(self, bl_start, bl_end, layout_start, layout_end):
        d = f'Block [0x{bl_start:0X}-0x{bl_end:0X}] is out of range [0x{layout_start:0X}-0x{layout_end:0X}]!'
        super().__init__(d)


class MemoryLayoutNoSpaceError(Exception):
    """Memory block intersects another one.
    """
    def __init__(self, src_start, src_end, target_start, target_end):
        d = f'Block [0x{src_start:0X}-0x{src_end:0X}] could not be append to layout [0x{target_start:0X}-0x{target_end:0X}]!'
        super().__init__(d)


class MemoryLayout:
    """Memory blocks holder with some functionality .

    Notes:
        - do not change layout start address or size after it was created;
        - add all memory regions before using methods that can change layout."""

    def __init__(self, begin_address, size):
        self._begin_address = begin_address
        self._size = size
        self._end_address = self._begin_address + self._size - 1
        self.regions = LinkedList()

    @classmethod
    def mem_blocks_layout_attributes(cls, mem_blocks_list: List[MemoryBlock]):
        """Returns minimal start address and total size of layout that specified blocks are compose.
        """
        min_address = 0
        size = 0
        max_end_address = 0
        if mem_blocks_list:
            min_begin_address = sys.maxsize
            for mb in mem_blocks_list:
                min_begin_address = min(min_begin_address, mb.begin_address())
                max_end_address = max(max_end_address, mb.end_address())
            size = max_end_address - min_begin_address + 1
        return min_begin_address, size

    @classmethod
    def from_mem_blocks(cls, mem_blocks_list: List[MemoryBlock]):
        """Returns new MemoryLayout that composed of specified memory blocks and has according start address and size.
        """
        min_address, size = cls.mem_blocks_layout_attributes(mem_blocks_list)
        ret = MemoryLayout(min_address, size)
        for mb in mem_blocks_list:
            ret.append_mem_block(mb)
        return ret

    def __eq__(self, other):
        """Instances are equal if they have equal begin address, size and all memory blocks are equal.

        NOTE: Memory blocks equality includes unused attributes equality!
        """
        if other:
            if self.begin_address() == other.begin_address() and self.size() == other.size():
                if self.regions.count() == other.regions.count():
                    ref_region = self.regions.head()
                    other_region = other.regions.head()
                    while ref_region:
                        ref_mem_block: MemoryBlock = ref_region.data()
                        other_mem_block: MemoryBlock = other_region.data()
                        if ref_mem_block == other_mem_block and ref_mem_block.is_unused() == other_mem_block.is_unused():
                            ref_region = ref_region.next()
                            other_region = other_region.next()
                        else:
                            return False
                    return True
        return False

    def begin_address(self):
        return self._begin_address

    def end_address(self):
        return self._end_address

    def size(self):
        return self._size

    def to_list(self):
        return self.regions.to_list()

    def append_mem_block(self, new_mem_block: MemoryBlock):
        """Add memory block in sorted way.
        """
        if new_mem_block.begin_address() < self._begin_address or new_mem_block.end_address() > self._end_address:
            raise MemoryLayoutError(new_mem_block.begin_address(), new_mem_block.end_address(), self._begin_address,
                                    self._end_address)

        first_region = self.regions.head()
        if first_region:
            if new_mem_block.end_address() < first_region.data().begin_address():
                self.regions.insert_before(first_region, new_mem_block)
                return
        else:
            self.regions.append(new_mem_block)
            return

        high_region = self.regions.tail()
        if new_mem_block.begin_address() > high_region.data().end_address():
            self.regions.insert_after(high_region, new_mem_block)
            return

        if self.regions.count() == 1:
            raise MemoryLayoutNoSpaceError(new_mem_block.begin_address(), new_mem_block.end_address(),
                                           self.begin_address(), self.end_address())

        low_region = first_region
        high_region = low_region.next()
        while high_region:
            if (new_mem_block.begin_address() > low_region.data().end_address()
                    and new_mem_block.end_address() < high_region.data().begin_address()):
                self.regions.insert_after(low_region, new_mem_block)
                return
            low_region = high_region
            high_region = high_region.next()

        raise MemoryLayoutNoSpaceError(new_mem_block.begin_address(), new_mem_block.end_address(),
                                       self.begin_address(), self.end_address())

    def fill_gaps(self):
        """Build defragmented layout with 'gaps' inserted in empty regions.

        Call this method when all memory blocks are already appended to layout.
        """
        free_address = self._begin_address
        region = self.regions.head()
        if not region:
            self.append_mem_block(MemoryBlock(begin_address=free_address, size=self._size, unused=True))
        else:
            while True:
                gap_size = region.data().begin_address() - free_address
                if gap_size > 0:
                    gap_region = MemoryBlock(begin_address=free_address, size=gap_size, unused=True)
                    self.append_mem_block(gap_region)
                free_address = region.data().end_address() + 1
                if free_address > self._end_address:
                    break
                region = region.next()
                if not region:
                    gap_size = self._end_address - free_address + 1
                    self.append_mem_block(MemoryBlock(begin_address=free_address, size=gap_size, unused=True))
                    break

    def merge_unused(self):
        """Merges all neighboring unused memory blocks.
        """
        region = self.regions.head()
        if not region:
            return

        merge_base = None
        while region:
            if not region.data().is_unused():
                merge_base = None
                region = region.next()
                continue
            else:
                if not merge_base:
                    merge_base = region
                    region = region.next()
                else:
                    new_size = region.data().end_address() - merge_base.data().begin_address() + 1
                    merged_region = MemoryBlock(begin_address=merge_base.data().begin_address(), size=new_size
                                                , identifier=merge_base.data().identifier(), unused=True)
                    new_region = self.regions.insert_before(merge_base, merged_region)
                    self.regions.remove(merge_base)
                    self.regions.remove(region)
                    merge_base = None
                    region = new_region


class MemoryLayoutPrinterConfig:
    """MemoryLayoutPrinter settings.
    """
    def __init__(self, is_bits=False, show_identifier=True, max_address_digits=0, no_headers=False,
                 cell_min_length=20, cell_max_length=45):
        self.show_identifier = show_identifier
        self.no_headers = no_headers
        self.cell_min_length = cell_min_length
        self.cell_max_length = cell_max_length

        if is_bits:
            self.show_address_range = True
            self.range_starts_from_higher_address = True
            self.address_base = 'dec'
            self.max_address_digits = 3
            self.range_separator = ':'
            self.brackets = 'square'
        else:
            self.show_address_range = True
            self.range_starts_from_higher_address = False
            self.address_base = 'hex'
            self.max_address_digits = max_address_digits
            self.range_separator = '-'
            self.brackets = 'parentheses'


class MemoryLayoutPrinterSettings:
    """Container for internal MemoryLayoutPrinter settings.
    """
    def __init__(self):
        self.text_offset = 1
        self.cell_vertical_separator = '-'
        self.cell_horizontal_separator = '|'
        self.ver_hor_cross_char = '+'
        self.unused_data_filler_char = 'X'


class MemoryLayoutPrinter:
    """Class that presents memory layouts different in some visual way.
    Using: add layouts that should be compared using 'add_layout' method, fill the empty spaces with
    fill_gaps method and call 'to_text' method to get comparing result as a text.
    """
    def __init__(self, config: MemoryLayoutPrinterConfig = MemoryLayoutPrinterConfig()):
        self._config = config
        self.loaded_layouts = []
        self.headers = []
        self._calculated_max_address_digits = 0
        self.settings = MemoryLayoutPrinterSettings()

    def add_layout(self, layout, header: str, position=-1):
        """Adds specified MemoryLayout instance to compare list to specified position with specified header.
        """
        if position < 0:
            self.loaded_layouts.append(layout)
            self.headers.append(header)
        else:
            count = len(self.loaded_layouts)
            if position > count:
                for i in range(count, position):
                    self.loaded_layouts.insert(None, i)
            self.loaded_layouts.insert(layout, position)
            self.headers.insert(position, header)

    def _get_mem_region_id(self, mem_reg: MemoryBlock):
        """Returns text that will be used as memory block identifier.
        """
        if mem_reg is None:
            return ''

        b = mem_reg.begin_address()
        e = mem_reg.end_address()
        d = (self._calculated_max_address_digits
             if self._config.max_address_digits == 0
             else self._config.max_address_digits)
        format_base_prefix = '0x' if self._config.address_base == 'hex' else ''
        format_base_suffix = f'0{d}X' if self._config.address_base == 'hex' else ''
        range_separator = self._config.range_separator
        open_bracket = '[' if self._config.brackets == 'square' else '('
        close_bracket = ']' if self._config.brackets == 'square' else ')'

        if b == e:
            address_range = f'{format_base_prefix}{b:{format_base_suffix}}'
        else:
            if self._config.range_starts_from_higher_address:
                address_range = f'{format_base_prefix}{e:{format_base_suffix}}{range_separator}' \
                                f'{format_base_prefix}{b:{format_base_suffix}}'
            else:
                address_range = f'{format_base_prefix}{b:{format_base_suffix}}{range_separator}' \
                                f'{format_base_prefix}{e:{format_base_suffix}}'

        ret = ''
        if self._config.show_identifier:
            ret += f'{mem_reg.identifier()}'
            if self._config.show_address_range:
                ret += f'{open_bracket}{address_range}{close_bracket}'
        else:
            if self._config.show_address_range:
                ret += f'{address_range}'
        return ret

    @staticmethod
    def _get_merged_addresses_list(ml_list, reverse=False):
        """Returns sorted list of start addresses of all the memory blocks in all appended layouts.
        """
        ret_set = set()
        for layout in ml_list:
            if layout:
                r = layout.regions.head()
                offsets_set = set()
                while r:
                    offsets_set.add(r.data().begin_address())
                    r = r.next()
                ret_set |= offsets_set
        return sorted(list(ret_set), reverse=reverse)

    def append_cell_line(self, cur_line, text):
        """Some magic.
        """
        if not text:
            return cur_line
        if not cur_line:
            return text
        if cur_line[-1] == text[0]:
            ret = cur_line + text[1:]
        else:
            if cur_line[-1] == ' ':
                ret = cur_line[:-1] + text
            elif cur_line[-1] == self.settings.cell_horizontal_separator and text[0] == self.settings.ver_hor_cross_char:
                ret = cur_line[:-1] + text
            else:
                ret = cur_line + text[1:]
        return ret

    def cell_data_only(self, text):
        return f'{text:^{self._config.cell_max_length}}'

    def get_cell(self, text, is_mem_block_start, is_endl, is_data=True):
        """Returns filled cell block.
        """
        ret = ['', '']
        cell_max_len = self._config.cell_max_length
        cross_char = self.settings.ver_hor_cross_char
        ver_char = self.settings.cell_horizontal_separator
        hor_char = self.settings.cell_vertical_separator
        prefix_suffix_char = ver_char if is_data else ' '

        if len(text) > self._config.cell_max_length:
            text = text[0:self._config.cell_max_length]

        text.replace('\n', '')

        ret[1] = prefix_suffix_char + self.cell_data_only(text) + prefix_suffix_char
        if is_mem_block_start:
            ret[0] = cross_char + cell_max_len * hor_char + cross_char
        else:
            ret[0] = ret[1]
        if is_endl:
            for idx in range(0, len(ret)):
                ret[idx] += '\n'
        return ret

    def to_text(self):
        """Returns string with data table representation.
        """
        all_addresses = self._get_merged_addresses_list(self.loaded_layouts)
        if all_addresses:
            self._calculated_max_address_digits = hex_digits(all_addresses[-1])
        else:
            return ''

        mem_regions_lists = []      # handy lists of regions
        for layout in self.loaded_layouts:
            if layout:
                mem_regions_lists.append(layout.to_list())
            else:
                mem_regions_lists.append(list())
        layouts_num = len(self.loaded_layouts)

        data_max_len = 0
        for i in range(0, len(mem_regions_lists)):
            mem_region = mem_regions_lists[i]
            for item in mem_region:
                data_max_len = max(data_max_len, len(self._get_mem_region_id(item)))
        header_max_len = max_strlen_in_list(self.headers)
        cell_data_max_len = max(data_max_len, header_max_len, self._config.cell_min_length)
        calculated_cell_max_len = cell_data_max_len + 2 * self.settings.text_offset

        # Save cell max length to use it in some internal methods
        self._config.cell_max_length = max(calculated_cell_max_len, self._config.cell_max_length)

        cell_max_len = self._config.cell_max_length    # handy short name

        unused_cell_str = self.settings.unused_data_filler_char * (self._config.cell_max_length - 2*self.settings.text_offset)
        empty_cell_str = ' ' * cell_max_len

        result = list()

        if not self._config.no_headers:
            result.append('')
            result.append('')
            for header_index in range(0, len(self.headers)):
                is_last_header_column = header_index == len(self.headers)-1
                header = self.headers[header_index]
                header_cell_strings = self.get_cell(header, is_mem_block_start=True, is_endl=is_last_header_column)
                result[0] = self.append_cell_line(result[0], header_cell_strings[0])
                result[1] = self.append_cell_line(result[1], header_cell_strings[1])

        layouts_cur_item_indexes = [0 for i in range(0, layouts_num)]

        is_first_address = True
        table_last_line = ''
        for address in all_addresses:
            cur_strings_block = ['', '']
            is_last_address = address == all_addresses[-1]

            for layout_index in range(0, layouts_num):
                cur_layout = self.loaded_layouts[layout_index]
                is_last_column = layout_index == layouts_num - 1
                if cur_layout:
                    cur_mem_regions_list = mem_regions_lists[layout_index]
                    cur_layout_item_index = layouts_cur_item_indexes[layout_index]

                    is_address_in_layout = cur_layout.begin_address() <= address <= cur_layout.end_address()
                    is_layout_items_just_finished = cur_layout_item_index == len(cur_mem_regions_list)
                    is_layouts_items_finished = cur_layout_item_index >= len(cur_mem_regions_list)
                else:
                    is_address_in_layout = False
                    is_layout_items_just_finished = False
                    is_layouts_items_finished = False

                if not is_address_in_layout:
                    cell_text = cell_max_len * ' '
                    is_separate_line_needed = is_layout_items_just_finished or is_first_address
                    cell_block = self.get_cell(cell_text, is_mem_block_start=is_separate_line_needed
                                               , is_endl=is_last_column, is_data=False)
                    cur_strings_block[0] = self.append_cell_line(cur_strings_block[0], cell_block[0])
                    cur_strings_block[1] = self.append_cell_line(cur_strings_block[1], cell_block[1])

                    if is_last_address:
                        cell_block = self.get_cell('', is_mem_block_start=False, is_endl=is_last_column, is_data=False)
                        table_last_line = self.append_cell_line(table_last_line, cell_block[0])

                    if is_layouts_items_finished:
                        layouts_cur_item_indexes[layout_index] += 1
                else:
                    # Use last layout item as data provider if it's still continues.
                    if is_layouts_items_finished:
                        cur_layout_item = cur_mem_regions_list[cur_layout_item_index - 1]
                    else:
                        cur_layout_item = cur_mem_regions_list[cur_layout_item_index]

                    new_data_cell_block_condition = address == cur_layout_item.begin_address()
                    if new_data_cell_block_condition:
                        if cur_layout_item.is_unused():
                            cell_text = unused_cell_str
                        else:
                            cell_text = self._get_mem_region_id(cur_layout_item)
                        layouts_cur_item_indexes[layout_index] += 1
                    else:
                        cur_layout_item = cur_mem_regions_list[cur_layout_item_index - 1]
                        if cur_layout_item.is_unused():
                            cell_text = unused_cell_str
                        else:
                            cell_text = empty_cell_str

                    cell_block = self.get_cell(cell_text, is_mem_block_start=new_data_cell_block_condition
                                               , is_endl=is_last_column)
                    cur_strings_block[0] = self.append_cell_line(cur_strings_block[0], cell_block[0])
                    cur_strings_block[1] = self.append_cell_line(cur_strings_block[1], cell_block[1])

                    if is_last_address:
                        cell_block = self.get_cell('', is_mem_block_start=True, is_endl=is_last_column, is_data=False)
                        table_last_line = self.append_cell_line(table_last_line, cell_block[0])

            result.extend(cur_strings_block)
            is_first_address = False

        result.append(table_last_line)
        return ''.join(result)

