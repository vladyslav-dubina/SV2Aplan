module union_example;
    typedef union {
        logic [31:0] full_word;
        logic [15:0] half_word[1:0];
        logic [7:0] bytes[3:0];
    } data_t;

    data_t my_data;

    initial begin
        my_data.full_word = 32'hDEADBEEF;
    end

endmodule