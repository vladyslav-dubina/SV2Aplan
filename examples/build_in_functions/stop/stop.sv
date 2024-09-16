module example_stop();
    int count;

    initial begin
        count = 0;
        while (count < 5) begin
            count++;

            if (count == 3) begin
                $stop;
            end
        end
    end
endmodule