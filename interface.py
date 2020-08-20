import abc

class Interface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def reset(self):
        pass

    @abc.abstractmethod
    def get_first_name_input(self):
        pass

    @abc.abstractmethod
    def get_misc_input(self, output):
        pass

    @abc.abstractmethod
    def get_selection(self, option_list):
        pass

    @abc.abstractmethod
    def get_mod(self):
        pass

    @abc.abstractmethod
    def display_message(self, text):
        pass

    @abc.abstractmethod
    def show_result(self, state):
        pass

    @abc.abstractmethod
    def get_save_choice(self):
        pass

    @abc.abstractmethod
    def get_dice(self, dice_count):
        pass

    @classmethod
    def __subclasshook__(cls, C):
        if cls is Interface:
            attrs = set(dir(C))
            if set(cls.__abstractmethods__) <= attrs:
                return True
        return NotImplemented
