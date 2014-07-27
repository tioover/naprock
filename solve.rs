use std::rc::Rc;
use std::num::abs;
use std::collections::HashSet;
use std::rand::{task_rng, Rng};
use std::comm;

type M = u8;
type N = int;
type Matrix = Vec<M>;
type Shape = (N, N);
type Value = int;
static X: N = 16;
static Y: N = 16;
static MAX_LOOP: uint = 10000u;
static TASK_NUM: uint = 3;
static BASE: uint = 500;
static THRESHOLD: uint = 200;


#[deriving(Clone)]
enum Step
{
    Select,
    Start,
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
    center: N,
    value: Value,
    steps: Vec<Step>,
}


impl Node
{
    fn print(&self)
    {
        let matrix = self.matrix.as_slice();
        let (x, y) = self.shape;
        for i in range(0, x as uint) {
            let j = y as uint;
            println!("{}", matrix.slice(i*j, i*j+j));
        }
        println!("value: {} center: [{}] {} step: {}\n",
                 self.value, self.center, (self.center / y + 1, self.center % y + 1), self.steps.len());
    }
}

fn valuation(matrix: &Matrix, shape: Shape) -> Value
{
    let mut value: Value = 0;
    let (x, y) = shape;
    for i in range(0, x*y) {
        let a = *matrix.get(i as uint) as int;
        value += abs(i/y - a/y) + abs((i % y) - (a % y));
    }
    value
}

fn turn(parent: Rc<Node>, step: Step) -> Option<Rc<Node>>
{
    let shape = parent.shape;
    let (x, y) = shape;
    let max = x*y;
    let center = parent.center;
    let mut matrix = parent.matrix.clone();
    let shift = match step {
        Up => if center >= y {Some(center - y)} else {None},
        Down => if center < max - y {Some(center + y)} else {None},
        Left => if center % y != 0 {Some(center - 1)} else {None},
        Right => if (center + 1) % y != 0 {Some(center + 1)} else {None},
        _ => fail!("turn arg error")
    };
    match shift {
        None => None,
        Some(shift) => {
            {
                let matrix_slice = matrix.as_mut_slice();
                matrix_slice.swap(center as uint, shift as uint);
            }
            Some(Rc::new(
                Node {
                    value: valuation(&matrix, parent.shape),
                    matrix: matrix,
                    shape: shape,
                    steps: parent.steps.clone().append_one(step),
                    center: shift,
                }
            ))
        }
    }
}


fn insert(open: &mut Vec<Rc<Node>>, node: Rc<Node>) -> ()
{
    let value = node.value;
    let len = open.len();

    if len == 0 || open.get(len-1).value >= value {
        open.push(node);
    }
    else if open.get(0).value < value {
        open.insert(0, node);
    }
    else {
        for i in range(0, len) {
            let n = len-1-i;
            if open.get(n).value >= node.value {
                open.insert(n, node);
                break;
            }
        }
    }
}

fn add(open: &mut Vec<Rc<Node>>, node: Rc<Node>) -> () {
    let mut shift = [Up, Down, Left, Right];
    task_rng().shuffle(shift);
    for step in shift.iter() {
        match turn(node.clone(), *step) {
            None => (),
            Some(new_node) => insert(open, new_node),
        };
    };
}


fn is_update(raw: &Rc<Node>, new: &Rc<Node>) -> bool {
    (new.value < raw.value) || (new.value == raw.value && new.steps.len() < raw.steps.len())
}


fn solve_with_node(
        root: Node,
        open: &mut Vec<Rc<Node>>,
        close: &mut HashSet<Vec<u8>>
    ) -> Node
{
    let mut update = 0;
    let mut solution = Rc::new(root);
    open.push(solution.clone());
    for i in range(0, MAX_LOOP) {
        if i > BASE && i - update > THRESHOLD {break;}
        match open.pop() {
            None => {println!("ERROR: Open empty."); break},
            Some(node) => {
                let value = node.value;
                if value == 0 {return node.deref().clone();}
                else if close.contains(&node.matrix) {continue;}
                else {close.insert(node.matrix.clone());}
                if is_update(&solution, &node) {
                    solution = node.clone();
                    update = i;
                };
                add(open, node);
            }
        }
    }
    solution.deref().clone()
}

fn solve_loop(root: Rc<Node>) -> Rc<Node>
{
    let (tx, rx): (Sender<Node>, Receiver<Node>) = comm::channel();
    let len = root.matrix.len();
    for id in range(0, TASK_NUM) {
        let task_tx = tx.clone();
        let new = root.deref().clone();
        spawn(proc() {
            let mut solutions = Vec::with_capacity(len/2);
            let mut open: Vec<Rc<Node>> = Vec::with_capacity(MAX_LOOP * 3);
            let mut close = HashSet::with_capacity(MAX_LOOP * 3);
            for i in range(0, len) {
                if i % TASK_NUM != id {continue}
                let mut now = new.clone();
                now.center = i as N;
                now.steps.push(Select);
                solutions.push(
                    solve_with_node(
                        now,
                        &mut open,
                        &mut close
                    )
                );
                open.clear();
                close.clear();
            }
            solutions.sort_by(|a, b| b.value.cmp(&a.value));
            match solutions.pop() {
                None => fail!("error in thread return"),
                Some(solution) => task_tx.send(solution),
            }
        });
    }
    let mut pre_solutions = Vec::with_capacity(len);
    for _ in range(0, TASK_NUM) {
        pre_solutions.push(rx.recv());
    }
    pre_solutions.sort_by(|a, b| b.value.cmp(&a.value));
    match pre_solutions.pop() {
        Some(solution) => Rc::new(solution),
        _ => fail!("error in solve_loop return.")
    }
}


fn solve(matrix: Matrix, shape: Shape, select_num: uint) -> Rc<Node>
{
    let mut root = Rc::new(Node {
        value: valuation(&matrix, shape),
        matrix: matrix,
        shape: shape,
        center: 0,
        steps: vec!(Start),
    }); // init
    for i in range(0, select_num) {
        root = solve_loop(root);
        if root.value == 0 {break;}
        println!("{}", i);
        root.print();
    }
    root
}


fn main()
{
    let mut matrix = Vec::from_fn((X*Y) as uint, |id| id as u8);
    {
        let m = matrix.as_mut_slice();
        task_rng().shuffle(m);
    }
    solve(matrix, (X, Y), 16).print();
}
