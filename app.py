import streamlit as st
from streamlit import legacy_caching

from wordle.game import Wordle


MARKDOWN_ANSWER_TEMPLATE = """
The correct answer was: <p style='color:Green;font-size:24px;text-align:center'><b>{answer}</b></p>
"""
WORDLE_RULES = """
* Guess the WORDLE in 6 tries.

* Each guess must be a valid 5 letter word.

* The colors of the letters show how close your guess was to the word.
    > <span style='color:Red'>RED</span> letters are not in the word.
    >
    > <span style='color:Yellow'>YELLOW</span> letters are in the word but in the wrong spot.
    >
    > <span style='color:Green'>GREEN</span> letters are in the word and in the correct spot.
"""


@st.cache(allow_output_mutation=True)
def new_game():
    return Wordle()


st.title("Wordle!")

with st.expander("Game Rules"):
    st.markdown(WORDLE_RULES, unsafe_allow_html=True)

game = new_game()
game.render_streamlit()

if not game._done:
    with st.form("Form"):
        guess = st.text_input("Enter your guess: ").strip()
        if st.form_submit_button("Submit"):
            game.step(guess)
            st.experimental_rerun()

else:
    if game._success:
        st.subheader("You won! :)")
    else:
        st.subheader("You lost. :(")
        st.markdown(
            MARKDOWN_ANSWER_TEMPLATE.format(answer=game._word.upper()),
            unsafe_allow_html=True,
        )

    if st.button("New Game"):
        legacy_caching.clear_cache()
        st.experimental_rerun()
