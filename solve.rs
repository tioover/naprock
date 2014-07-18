use std::rc::Rc;
use std::num::abs;
type N = int;
type Parent = Option<Rc<Node>>;
type Matrix = Vec<N>;
static X: N = 3;
static Y: N = 3;


enum Step {
    Up,
    Down,
    Left,
    Right,
    Start,
}


struct Node {
    matrix: Box<Matrix>,
    shape: (N, N),
    parent: Parent,
    center: N,
    depth: N,
    value: f32,
    step: Step,
}

fn new(matrix: Box<Matrix>, shape: (N, N), center: N) -> Node {
    let value = valuation(matrix, shape);
    Node {
        matrix: matrix,
        shape: shape,
        parent: None,
        center: center,
        depth: 0,
        value: value,
        step: Start
    }
}

fn valuation(matrix: &Matrix, shape: (N, N)) -> f32 {
    let mut value = 0i;
    let (x, y) = shape;
    for i in range(0, x*y) {
        let a = matrix.get(i as uint);
        value += abs(i/y - a/y) + abs((i % y) - (a % y));
    }
    value as f32
}

fn spread(parent: Rc<Node>, step: Step) -> Option<Rc<Node>> {
    let (x, y) = parent.shape;
    let max = x*y;
    let center = parent.center;
    let mut new_center = center;
    let mut matrix = parent.matrix.clone();
    let new_node = Rc::new({
    });
    let shift: Option<N> = match step {
        Up => {
            let shift = center - x;
            if shift >= 0 {Some(shift)} else {None}
        },
        Down => {
            let shift = center + x;
            if shift < max {Some(shift)} else {None}
        },
        Left => {
            let shift = center - 1;
            if center % y != 0 {Some(shift)} else {None}
        },
        Right => {
            let shift = center + 1;
            if shift % y != 0 {Some(shift)} else {None}
        },
        Start => fail!("Start?")
    };
    match shift {
        None => None,
        Some(shift) => {
            {
                let c = center as uint;
                let s = shift as uint;
                let matrix_slice = matrix.as_mut_slice();
                let swap = matrix_slice[c];
                matrix_slice[c] = matrix_slice[s];
                matrix_slice[s] = swap;
            }
            let value = valuation(matrix, parent.shape);
            Some(Rc::new(Node{
                matrix: matrix,
                shape: parent.shape,
                parent: Some(parent.clone()),
                center: shift,
                depth: parent.depth + 1,
                value: value,
                step: step,
            }))
        }
    }
}

fn main() {
}
