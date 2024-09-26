module pow_example;
    real input_val;
    real result;
    initial begin
        input_val = 1.2;
        result = $pow(input_val, 2);
        result = $pow(input_val, 3);
    end
endmodule