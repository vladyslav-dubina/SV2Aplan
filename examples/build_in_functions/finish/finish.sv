module example_finish();
    int count;

    initial begin
        count = 0;

        while (count < 5) begin
            count++;

            if (count == 3) begin
                $finish;
            end
        end
    end
endmodule