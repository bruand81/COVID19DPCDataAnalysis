import unicodedata
import string

class Utils:
    __valid_filename_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    __char_limit = 255

    def clean_filename(self, filename, whitelist=None, replace=' '):
        whitelist = whitelist if whitelist is not None else self.__valid_filename_chars

        # replace spaces
        for r in replace:
            filename = filename.replace(r, '_')

        # keep only valid ascii chars
        cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode()

        # keep only whitelisted chars
        cleaned_filename = ''.join(c for c in cleaned_filename if c in whitelist)
        if len(cleaned_filename) > self.__char_limit:
            print(
                "Warning, filename truncated because it was over {}. Filenames may no longer be unique".format(
                    self.__char_limit))
        return cleaned_filename[:self.__char_limit]