module function_example;

    function int factorial(input int n);
        begin
            if (n <= 1)
                factorial = 1;
            else
                factorial = n * factorial(n - 1);
        end
    endfunction

    initial begin
        int number = 5;
        int result;

        result = factorial(number);
    end

endmodule
