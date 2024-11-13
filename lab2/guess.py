from random import randint

user_name = input("What is your name? ")
print("Hello", user_name)

secret_number = randint(1, 99)
user_guess = int(input("Your guess? "))
guess_count = 1

while user_guess != secret_number:
    if user_guess < secret_number:
        print("Too small. Try again.")

    if user_guess > secret_number:
        print("Too large. Try again.")

    user_guess = int(input("Your guess? "))
    guess_count += 1

print("Correct! You guessed", guess_count, "time(s).")
