# -*- coding: utf-8 -*-

    def get_text_by_index(self, index):
        famous_text = ""
        if (index < 1):
            return famous_text
        fd = codecs.open(dbmenus.famous_file, mode='r', encoding="utf-8")
        item_num = 0
        found_item = False
        while True:
            line = fd.readline()
            if not line:
                break
            if (line.find(CONTENT_ITEM_TAG) != -1):
                item_num = item_num + 1
                if (item_num == index):
                    found_item = True
                    continue
                if (found_item == True):
                    break
            else:
                if (found_item == True):
                    famous_text = famous_text + line
        
        famous_text = famous_text.decode("utf-8")
        return famous_text;
