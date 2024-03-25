import random


def generate_multiplication_question(min_value, max_value):
    multiplicand1 = random.randint(min_value, max_value)
    multiplicand2 = random.randint(min_value, max_value)
    question_text = f"{multiplicand1} * {multiplicand2} = "
    correct_answer = multiplicand1 * multiplicand2
    return question_text, correct_answer
