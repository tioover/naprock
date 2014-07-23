use std::rc::Rc;
use std::num::abs;
use std::collections::HashMap;
//use std::collections::PriorityQueue;

type N = int;
type Parent = Option<Rc<Node>>;
type Matrix = Rc<Vec<N>>;
type Shape = (N, N);
type Value = int;
static X: N = 10;
static Y: N = 10;


#[deriving(Clone)]
enum Step
{
    Select,
    Left,
    Right,
    Up,
    Down,
}

#[deriving(Clone)]
struct Node
{
    matrix: Matrix,
    shape: Shape,
    parent: Parent,
    center: N,
    depth: N,
    value: Value,
    step: Step,
}

impl Node
{
    fn new(parent: Rc<Node>, matrix: Matrix, step: Step, center: N) -> Node
    {
        let value = Node::valuation(matrix.clone(), parent.shape);
        Node {
            matrix: matrix,
            shape: parent.shape,
            parent: Some(parent.clone()),
            center: center,
            depth: parent.depth + 1,
            value: value,
            step: step,
        }
    }

    fn new_root(matrix: Matrix, shape: Shape, center: N) -> Node
    {
        let value = Node::valuation(matrix.clone(), shape);
        Node {
            matrix: matrix,
            shape: shape,
            center: center,
            depth: 0,
            value: value,
            step: Select,
            parent: None,
        }
    }

    fn valuation(matrix: Matrix, shape: Shape) -> Value
    {
        let mut value = 0i;
        let (x, y) = shape;
        for i in range(0, x*y) {
            let a = matrix.get(i as uint);
            value += abs(i/y - a/y) + abs((i % y) - (a % y));
        }
        value as Value
    }

    fn print(&self)
    {
        let matrix = self.matrix.as_slice();
        let (x, y) = self.shape;
        for i in range(0, x as uint) {
            let j = y as uint;
            println!("{}", matrix.slice(i*j, i*j+j));
        }
        println!("value: {} center: [{}] {}\n",
                 self.value, self.center, (self.center / y + 1, self.center % y + 1));
    }
}


fn turn(parent: Rc<Node>, step: Step) -> Option<Rc<Node>>
{
    let (x, y) = parent.shape;
    let max = x*y;
    let center = parent.center;
    let mut matrix = parent.matrix.deref().clone();
    let shift = match step {
        Up => {
            let shift = center - y;
            if shift >= 0 {Some(shift)} else {None}
        },
        Down => {
            let shift = center + y;
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
        _ => fail!("turn arg error")
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
            Some(Rc::new(Node::new(parent, Rc::new(matrix), step, shift)))
        }
    }
}


fn insert(open: &mut Vec<Rc<Node>>, node: Rc<Node>) -> ()
{
    match open.len() {
        0 => open.push(node),
        len => {
            for i in range(0u, len) {
                if open.get(i).value < node.value {
                    open.insert(i, node.clone());
                    break;
                }
                else if i == len - 1 {
                    open.push(node.clone());
                }
            }
        }
    };
}


fn add(open: &mut Vec<Rc<Node>>, node: Rc<Node>) -> () {
    let step = [Up, Down, Left, Right];
    for i in range(0u, 4) {
        match turn(node.clone(), step[i]) {
            None => {},
            Some(new_node) => {
                //println!("add {}", match i {0 => "up", 1 => "down", 2 => "left", 3 => "right", _ => "erro"});
                insert(open, new_node)
            },
        };
    };
}


fn is_update(raw: &Rc<Node>, new: &Rc<Node>) -> bool {
    (new.value < raw.value) || (new.value == raw.value && new.depth < raw.depth)
}


fn solve_with_node(root: Rc<Node>) -> Rc<Node>
{
    let max_loop = 1000u;
    let mut open: Vec<Rc<Node>> = Vec::new();
    let mut close = HashMap::new();
    let mut solution = root.clone();
    open.push(root);
    for _ in range(0, max_loop) {
        match open.pop() {
            None => {println!("ERROR: Open empty."); break},
            Some(node) => {
                let value = node.value;
                if value == 0 {return node;}
                else if close.contains_key(&node.matrix) {continue;} // TODO: update
                else {close.insert(node.matrix.clone(), node.clone());}
                if is_update(&solution, &node) {solution = node.clone()};
                add(&mut open, node);
            }
        }
    }
    solution
}


fn solve_loop(root: Rc<Node>) -> Rc<Node>
{
    let mut solution = solve_with_node(root.clone());
    for i in range(0, root.matrix.len() as N) {
        let mut now = root.deref().clone();
        now.center = i;
        now.parent = Some(root.clone());
        now.depth += 1;
        now.step = Select;
        let now_solution = solve_with_node(Rc::new(now));
        if now_solution.value == 0 {return now_solution;}

        if is_update(&solution, &now_solution) {
            solution = now_solution;
        }
    }
    solution
}


fn solve(matrix: Rc<Vec<N>>) -> Rc<Node>
{
    let mut root = Rc::new(Node::new_root(matrix, (X, Y), 0));
    for _ in range(0, 16u) {
        root = solve_loop(root);
        if root.value == 0 {break;}
        root.print();
    }
    root
}


fn main()
{
    let mut matrix: Vec<N> = range(0, X*Y).collect();
    {
        use std::rand::{task_rng, Rng};
        let m = matrix.as_mut_slice();
        let mut rng = task_rng();
        rng.shuffle(m);
    }
    solve(Rc::new(matrix)).print();
}
