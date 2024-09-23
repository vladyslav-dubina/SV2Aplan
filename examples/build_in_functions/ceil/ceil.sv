module ceil_example;
    real input_val;
    real result;
    initial begin
        input_val = 1.2;
        
        result = $ceil(1);
        result = $ceil(input_val);
        
    end
endmodule