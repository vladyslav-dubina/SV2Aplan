module function_example;

    function int add(input int x, input int y);
        begin
            add = x + y;
        end
    endfunction

    function int multiply(input int x, input int y);
        begin
            return x * y;
        end
    endfunction

    initial begin
        int a, b, result_add, result_mul;

        a = 10;
        b = 5;

        result_add = add(a, b);

        result_mul = multiply(a, b);
    end

endmodule
