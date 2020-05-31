
module cnt1_tb;


//========================================
//
// Instantiation: cnt1
//
//========================================
wire  [4:0] st, addr;
wire        we, csn;
reg         req = 0;
reg         rst = 1;

reg         clk = 0;
always #5 clk = ~clk;

reg         en  = 0;
initial forever begin
    repeat(9) @(negedge clk);
    en = 1;
    @(negedge clk) en = 0;
end

cnt1  inst (
    .addr( addr), // O [4:0]
    .st  ( st  ), // O [4:0]
    .csn ( csn ), // O
    .we  ( we  ), // O
    .req ( req ), // I
    .en  ( en  ), // I
    .rst ( rst ), // I
    .clk ( clk )  // I
); // instantiation of cnt1

initial begin
    $dumpvars();
    $monitor($time, " %h %h %h %h %h %h %h", rst, en, req, we, st, csn, addr);

    #20 rst = 0;
    #20 req = 1;
    #3000 $finish;
end

endmodule
