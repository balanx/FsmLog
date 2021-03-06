
module filt3 (
  output reg       y = 1'd0,
  input            i,

  input    rst,
  input    clk
);


localparam
Z0 = 3'd0,
Z1 = 3'd1,
Z2 = 3'd2,
E0 = 3'd3,
E1 = 3'd4,
E2 = 3'd5;

reg [2:0] state, next;
always @(posedge clk or posedge rst)
if (rst)
  state <= Z0;
else
  state <= next;


always @(*) begin
  next = state;

  case(state)
    Z0 :
      if (i==1'b1)
        next = Z1;
    Z1 :
      if (i==1'b1)
        next = Z2;
      else if (i==1'b0)
        next = Z0;
    Z2 :
      if (i==1'b1)
        next = E0;
      else if (i==1'b0)
        next = Z0;
    E0 :
      if (i==1'b0)
        next = E1;
    E1 :
      if (i==1'b0)
        next = E2;
      else if (i==1'b1)
        next = E0;
    E2 :
      if (i==1'b0)
        next = Z0;
      else if (i==1'b1)
        next = E0;
    default :
        next = Z0;
  endcase
end

always @(posedge clk or posedge rst)
if (rst) begin
  y <= 1'd0;
end
else begin
//following 0,1
  //y <= 1'd0;

    case (state)
      Z0 : begin
        y <= 1'b0;
      end
      E0 : begin
        y <= 1'b1;
      end
    endcase
end

endmodule // @FsmLog
