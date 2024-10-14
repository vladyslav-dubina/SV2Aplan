module floor_example;
    real input_val;
    real result;
    initial begin
        input_val = 1.2;
        
        result = $floor(1);
        result = $floor(input_val);
        
    end
endmodule