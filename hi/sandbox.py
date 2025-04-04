def cube_number(n):
    result = 0
    for i in range(n):
        for j in range(n * n):  # This loop simulates the cubic complexity
            result += 1
    return result

number = 2  # Example number to cube
result = cube_number(number)
print(f"Cube of {number} is: {result}")


