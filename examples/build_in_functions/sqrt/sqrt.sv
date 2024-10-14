module sqrt_example;
    int input_val;
    real result;
    initial begin
        input_val = -1;
        
        result = $sqrt(25);
        result = $sqrt(input_val);
        
    end
endmodule