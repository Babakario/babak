from calculator import add, subtract, multiply, divide

def main():
    try:
        num1_str = input("Enter the first number: ")
        num1 = float(num1_str)

        operation = input("Enter the operation (+, -, *, /): ")

        num2_str = input("Enter the second number: ")
        num2 = float(num2_str)

        if operation == '+':
            result = add(num1, num2)
        elif operation == '-':
            result = subtract(num1, num2)
        elif operation == '*':
            result = multiply(num1, num2)
        elif operation == '/':
            result = divide(num1, num2)
        else:
            print("Invalid operation. Please use +, -, *, or /.")
            return

        print(f"{num1} {operation} {num2} = {result}")

    except ValueError:
        print("Invalid input. Please enter numbers only.")
    except ZeroDivisionError:
        print("Error: Cannot divide by zero.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
