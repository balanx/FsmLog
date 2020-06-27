
module filt4 (
  output reg       y = 1'd0,
  input            i,

  input    en,
  input    clk
);

reg [3:0] cnt = 4'd0;

localparam
Z0 = 2'd0,
Z1 = 2'd1,
E0 = 2'd2,
E1 = 2'd3;

reg [1:0] state, next;
always @(posedge clk)
if (en == 1'b1)
  state <= next;


always @(*) begin
  next = state;

  case(state)
    Z0 :
      if (i==1'b1)
        next = Z1;
    Z1 :
      if (cnt>4'd9)
        next = E0;
      else if (i==1'b0)
        next = Z0;
    E0 :
      if (i==1'b0)
        next = E1;
    E1 :
      if (cnt>4'd9)
        next = Z0;
      else if (i==1'b1)
        next = E0;
    default :
        next = Z0;
  endcase
end

always @(posedge clk) begin
//following 0,1

  if (en == 1'b1) begin
  //y <= 1'd0;
    cnt <= 4'd0;

    case (state)
      Z0 : begin
        y <= 1'b0;
      end
      E0 : begin
        y <= 1'b1;
      end
      Z1 : begin
        cnt <= cnt+1'b1;
      end
      E1 : begin
        cnt <= cnt+1'b1;
      end
    endcase
  end
end

endmodule // @FsmLog
