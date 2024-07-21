import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.webdriver import WebDriver
from quickdraw import QuickDrawData
from math import floor
import logging
import random
from enum import Enum

qd = QuickDrawData()

class GameState(Enum):
    GUESSING = "GUESSING"
    DRAWING = "DRAWING"
    pass


def main_create():
    logging.info("main create")
    options = webdriver.FirefoxOptions()
    # options.add_argument("--headless")
    with webdriver.Firefox(options=options) as driver:
        join_website(driver)
        set_name(driver)
        create_lobby(driver)
        load_ads(driver)
        remove_ads(driver)
        invite_link = get_invite_link(driver)
        set_custom_words(driver)
        print("please join the lobby:", invite_link)
        wait_for_player_join(driver)
        start_game(driver)
        game_loop(driver)
        input("end")
        pass
    pass


def main_join(invite_link: str):
    logging.info("main join")
    print(invite_link)
    pass


def join_website(driver: WebDriver):
    logging.info("join website")
    driver.get("https://skribbl.io/")
    assert driver.title == "skribbl - Free Multiplayer Drawing & Guessing Game"
    pass


def create_lobby(driver: WebDriver):
    logging.info("create lobby")
    elem_create = driver.find_element(By.CLASS_NAME, "button-create")
    elem_create.click()
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#game-word .description.waiting")
        )
    )
    pass


def set_name(driver: WebDriver):
    logging.info("set name")
    driver.find_element(By.CLASS_NAME, "input-name").send_keys("skribblio-bot")
    pass


def set_custom_words(driver: WebDriver):
    logging.info("set custom words")
    WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, "item-settings-customwordsonly"))
    )
    WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, "item-settings-customwords"))
    )
    elem_custom_words_only = driver.find_element(By.ID, "item-settings-customwordsonly")
    elem_custom_words_only.click()
    elem_custom_words = driver.find_element(By.ID, "item-settings-customwords")
    elem_custom_words.click()
    categories = ",".join(qd.drawing_names)
    elem_custom_words.send_keys(categories)
    pass


def load_ads(driver: WebDriver):
    logging.info("load ads")
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".adsbygoogle.adsbygoogle-noablate")
        )
    )
    # WebDriverWait(driver, 30).until(
    #     EC.presence_of_element_located(
    #         (By.ID, "ad_position_box")
    #     )
    # )
    pass


def remove_ads(driver: WebDriver):
    logging.info("remove ads")
    driver.execute_script(
        """
        const elements = document.getElementsByClassName("adsbygoogle")
        for (const element of elements) {
            element.parentNode.removeChild(element)
        }
        """
    )
    # const element = document.getElementById("ad_position_box")
    # element.parentNode.removeChild(element)
    pass


def get_invite_link(driver: WebDriver) -> str:
    logging.info("get invite link")
    driver.find_element(By.ID, "copy-invite").click()
    WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, "item-settings-customwords"))
    )
    elem_custom_words = driver.find_element(By.ID, "item-settings-customwords")
    elem_custom_words.click()
    elem_custom_words.send_keys(Keys.CONTROL, "v")
    invite_link = driver.find_element(By.ID, "item-settings-customwords").get_attribute(
        "value"
    )
    elem_custom_words.send_keys(Keys.CONTROL, "a", Keys.DELETE)
    return invite_link


def wait_for_player_join(driver: WebDriver):
    logging.info("waiting for player join")
    try:
        WebDriverWait(driver, 600).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".player.odd.last"))
        )
        logging.info("player joined")
    except Exception as e:
        logging.error("Error: player did not join in time (10 minutes)")
        sys.exit(1)
    pass


def start_game(driver: WebDriver):
    logging.info("start game")
    elem_play = driver.find_element(By.ID, "start-game")
    elem_play.click()
    pass


def game_loop(driver: WebDriver):
    logging.info("game loop")
    is_active = True
    while is_active:
        wait_for_round_start(driver)
        game_state = get_game_state(driver)
        print("game_state", game_state)
        match game_state:
            case GameState.DRAWING:
                word = choose_word(driver)
                print("chosen word", word)
                draw_word(driver, word)
                pass
            case GameState.GUESSING:
                guess_word(driver)
                pass
            case default:
                is_active = False
                raise Exception("Unknown game state", default)
        pass
    logging.info('Game Over')
    pass


def get_game_state(driver: WebDriver) -> GameState:
    logging.info("get game state")
    wait = WebDriverWait(driver, 3)
    element = (By.CSS_SELECTOR, ".text.show")
    try:
        wait.until(EC.presence_of_element_located(element))
    except Exception as e:
        check_game_over(driver)
    wait.until(EC.visibility_of_element_located(element))
    text_show = driver.find_element(By.CSS_SELECTOR, ".text.show")
    if "Round" in text_show.text:
        wait.until_not(EC.visibility_of_element_located(element))
        wait.until(EC.visibility_of_element_located(element))
        pass
    text_show = driver.find_element(By.CSS_SELECTOR, ".text.show")
    if "is choosing a word!" in text_show.text:
        return GameState.GUESSING
    return GameState.DRAWING


def check_game_over(driver: WebDriver) -> bool:
    logging.info("check game over")
    winner = driver.find_element(By.CSS_SELECTOR, ".result>.message>.winner-name")
    return len(winner.text) != 0


def wait_for_round_start(driver: WebDriver):
    logging.info("wait for round start")
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#game-word .description.waiting")
        )
    )
    pass


def guess_word(driver: WebDriver):
    logging.info("guess word")
    input("guessed word")
    # word_length = get_word_length(driver)
    # global CATEGORIES
    # for category in CATEGORIES.split(",\n"):
    #     if len(category) != word_length:
    #         continue
    #     elem_input = driver.find_element(By.XPATH, "/html/body/div[3]/div[1]/div[6]/div/form/input")
    #     elem_input.click()
    #     elem_input.send_keys(category, Keys.ENTER)
    #     pass
    pass


def get_word_length(driver: WebDriver):
    logging.info("get word length")
    elem_word_length = driver.find_element(By.CLASS_NAME, "word-length")
    word_length = int(elem_word_length.text)
    return word_length


def choose_word(driver: WebDriver) -> str:
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".words.show > .word"))
    )
    words = driver.find_elements(by=By.CSS_SELECTOR, value=".words.show > .word")
    assert len(words) == 3
    random_index = random.random() * 3
    chosen_word = words[floor(random_index)]
    chosen_word.click()
    return chosen_word.text


def draw_word(driver: WebDriver, word: str):
    logging.info("draw word")
    assert word in qd.drawing_names
    WebDriverWait(driver, 60).until_not(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#game-canvas > .overlay.show")
        )
    )
    canvas = driver.find_element(by=By.CSS_SELECTOR, value="#game-canvas > canvas")
    width = canvas.size["width"]
    height = canvas.size["height"]
    drawing = qd.get_drawing(word)
    for stroke in drawing.strokes:
        action = webdriver.ActionChains(driver).move_to_element_with_offset(
            canvas, -width // 2 + 50, -height // 2 + 50
        )
        initial_coord = stroke[0]
        action.move_by_offset(initial_coord[0], initial_coord[1])
        action.click_and_hold()
        for i in range(1, len(stroke)):
            prev_coord = stroke[i - 1]
            coord = stroke[i]
            x_offset = coord[0] - prev_coord[0]
            y_offset = coord[1] - prev_coord[1]
            action.move_by_offset(x_offset, y_offset)
            pass
        action.release()
        action.perform()
        pass
    print("drawing complete")
    pass


def print_usage():
    logging.info(
        """
            Usage: python main.py <function>
            functions:
                create
                join <invite link>
            """
    )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    function = sys.argv[1]
    if function == "create":
        main_create()
    elif function == "join":
        if len(sys.argv) != 2:
            print_usage()
            sys.exit(1)
        invite_link = sys.argv[1]
        main_join(invite_link)
    else:
        print_usage()
        sys.exit(1)
    pass
