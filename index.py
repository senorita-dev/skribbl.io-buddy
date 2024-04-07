import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.webdriver import WebDriver
import random
from math import floor
from quickdraw import QuickDrawData


qd = QuickDrawData()


def run(invite_link):
    with webdriver.Firefox() as driver:
        join_game(driver, invite_link)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#game-word .description.waiting")
            )
        )
        print("Joined Game, waiting for host to start game...")
        WebDriverWait(driver, 60).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#game-canvas > .overlay-content > .text.show"),
                "Choose a word",
            )
        )
        print("Game started!")
        game_state = get_game_state(driver)
        match game_state:
            case "Choose a word":
                # Buddy is choosing a word and drawing
                word = choose_word(driver)
                draw_word(driver, word)
                pass
            case _:
                # Buddy is guessing the word
                pass
        input("end")
        pass
    pass


def join_game(driver: WebDriver, invite_link: str):
    driver.get(invite_link)
    assert driver.title == "skribbl - Free Multiplayer Drawing & Guessing Game"
    elem_name = driver.find_element(By.CLASS_NAME, "input-name")
    elem_name.send_keys("skribblio-bot")
    elem_play = driver.find_element(By.CLASS_NAME, "button-play")
    elem_play.click()
    pass


def wait_for_game_start(driver: WebDriver):
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#game-word .description.waiting")
        )
    )
    pass


def get_game_state(driver: WebDriver) -> str:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".text.show"))
    )
    elem_state = driver.find_element(By.CSS_SELECTOR, ".text.show")
    return elem_state.text


def choose_word(driver: WebDriver) -> str:
    words = driver.find_elements(by=By.CSS_SELECTOR, value=".words.show > .word")
    assert len(words) == 3
    random_index = random.random() * 3
    chosen_word = words[floor(random_index)]
    chosen_word.click()
    return chosen_word.text


def draw_word(driver: WebDriver, word: str):
    print("draw word", word)
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
        action = webdriver.ActionChains(driver).move_to_element_with_offset(canvas, -width // 2 + 50, - height // 2 + 50)
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


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python index.py <invite link>")
        sys.exit(1)
    invite_link = sys.argv[1]
    run(invite_link)
    pass
