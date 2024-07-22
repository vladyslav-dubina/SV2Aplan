module task_example;

    function add(input int x, input int y);
        begin
            add = x + y;
        end
    endfunction

    function subtract(input int x, input int y);
        begin
            subtract = x - y;
        end
    endfunction


    initial begin
        int a, b, result;
        a = 10;
        b = 5;

        result = add(a,b) + subtract(a,b);
    end

endmodule