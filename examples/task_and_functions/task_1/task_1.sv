module task_example;
    int a, b, result_add, result_sub;

    task add(input int x, input int y, output int z);
        begin
            z = x + y;
        end
    endtask

    task subtract(input int x, input int y, output int z);
        begin
            z = x - y;
        end
    endtask

    task calculate(input int a, input int b, output int result_add, output int result_mul);
        int temp_sum;
        begin
            add(a, b, temp_sum);
            multiply(a, b, result_mul);
            result_add = temp_sum;
        end
    endtask

    initial begin
        a = 10;
        b = 5;

        add(a, b, result_add);

        subtract(a, b, result_sub);
    end

endmodule
