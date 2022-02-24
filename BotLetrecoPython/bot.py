from botcity.web import WebBot
from botcity.web.browsers.chrome import default_options
import random
import re


class Bot(WebBot):
    def action(self, execution=None):
        self.headless = False
        self.driver_path = 'C:\\Users\\joaov\\Downloads\\Programas\\chrome\\chromedriver.exe'

        # REMOVENDO MENSAGENS DO LOG
        def_options = default_options(
            headless=self.headless,
            user_data_dir=None
        )
        def_options.add_argument('--log-level=3')
        self.options = def_options

        self.start_game()
        input('Press any key to exit: ')


    def start_game(self):
        words_list = []
        with open("resources/words_list.txt", "r") as file:
            for line in file:
                if '-' not in line and len(line) == 6:
                    words_list.append(line.replace('\n', ''))
        
        self.browse("https://www.gabtoschi.com/letreco/")

        total_attempts = 0
        words = words_list
        while total_attempts < 6:
            if words:
                # Choose a random word to start
                random_word = random.choice(words)
                print("Attempt: " + str(total_attempts + 1) + " | Word: " + random_word)

                # Insert the word 
                self.insert_word(random_word, total_attempts)

                # Check the result and do the filters for the next attempt
                filtered_list = self.check_result(words, random_word, total_attempts)
                words = filtered_list

                self.wait(2000)
                total_attempts += 1

                try:
                    result = self.execute_javascript('return document.getElementsByClassName("text-center mb-3 win-text")[0].textContent;')
                    if result:
                        print("\nYou Win!\n")
                        break
                except:
                    continue
            else:
                print("Game Over! - word not found")
                break
            

    def insert_word(self, word, attempt):
        self.execute_javascript(f"""
            var word = "{word}";
            var inputs = document.getElementsByClassName("d-flex justify-content-center mb-3")[{attempt}].getElementsByTagName("div");
            var keyboard_keys = document.getElementsByClassName("px-lg-5 px-2")[0].getElementsByTagName("button");

                for(var i=0; i<inputs.length; i++){{
                    for(var j=0; j<keyboard_keys.length; j++){{
                        if(keyboard_keys[j].textContent === word[i])
                            keyboard_keys[j].click();
                    }}
                }}
            """)
        self.execute_javascript('document.getElementsByClassName("keyboard-button rounded action-button")[1].click();')

    
    def check_result(self, words_list, word, attempt):
        # Filtering the word list with the displaced characters
        displaced_letters = self.execute_javascript(f"""
            var word = "{word}";
            var displaced_letters = {{}};
            var inputs = document.getElementsByClassName("d-flex justify-content-center mb-3")[{attempt}].getElementsByTagName("div");
            
                for(var i=0; i<inputs.length; i++){{
                    if(inputs[i].className.includes("displaced") || inputs[i].className.includes("right"))
                        displaced_letters[i] = word[i];
                }}
                return displaced_letters;
            """)
        if displaced_letters:
            filter = set()
            for letter in displaced_letters.values():
                if letter not in filter:
                    filter.add(letter)
            filtered_list = [word for word in words_list if filter.issubset(word)]
            words_list = filtered_list

        # Filtering the word list with the wrong characters
        wrong_letters = self.execute_javascript(f"""
            var word = "{word}";
            var wrong_letters = [];
            var inputs = document.getElementsByClassName("d-flex justify-content-center mb-3")[{attempt}].getElementsByTagName("div");
            
                for(var i=0; i<inputs.length; i++){{
                    if(inputs[i].className.includes("wrong"))
                        wrong_letters.push(word[i]);
                }}
                return wrong_letters;
            """)
        if wrong_letters:
            regex = ''
            for letter in wrong_letters:  
                if letter not in displaced_letters.values():
                    regex = regex + letter
            if regex:
                filter_regex = f"\\b[^{regex}]+\\b"
                words_list = self.filter_list(words_list, filter_regex)

        # Filtering the word list with the correct characters
        correct_letters = self.execute_javascript(f"""
            var word = "{word}";
            var correct_letters = {{}};
            var inputs = document.getElementsByClassName("d-flex justify-content-center mb-3")[{attempt}].getElementsByTagName("div");
            
                for(var i=0; i<inputs.length; i++){{
                    if(inputs[i].className.includes("right"))
                        correct_letters[i] = word[i];
                }}
                return correct_letters;
            """)
        if correct_letters:
            new_list = []
            for word in words_list:
                valid_word = True
                for key in correct_letters.keys():
                    if word[int(key)] != correct_letters[key]:
                        valid_word = False
                        break
                if valid_word:
                    new_list.append(word)
            words_list = new_list

        # Last filter
        out_of_position = { k : displaced_letters[k] for k in set(displaced_letters) - set(correct_letters) }
        if out_of_position:
            new_list = []
            for word in words_list:
                valid_word = True
                for key in out_of_position.keys():
                    if word[int(key)] == out_of_position[key]:
                        valid_word = False
                        break
                if valid_word:
                    new_list.append(word)
            words_list = new_list
        return words_list

    
    def filter_list(self, words_list, regex_pattern):
        pattern = re.compile(regex_pattern)
        filtered_list = [word for word in words_list if pattern.match(word)]
        return filtered_list


    def not_found(self, label):
        print(f"Element not found: {label}")


if __name__ == '__main__':
    Bot.main()
