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

    task calculate(input int in_a, input int in_b, output int out_result_add, output int out_result_sub);
        int temp_sum;
        begin
            add(in_a, in_b, temp_sum);
            subtract(in_a, in_b, out_result_sub);
            out_result_add = temp_sum;
        end
    endtask

    initial begin
        a = 10;
        b = 5;

        calculate(a, b, result_add, result_sub);
    end

endmodule