import React, {Component} from 'react';

import Form from '../../utils/Form';
import ConstantsCss from '../Constants-CSS';
import { eventHandler } from '../Utils';
import { Save, Delete, Edit, Cancel } from '../../components/dessign/icons';
import { Normal, Primary, Danger } from '../../components/dessign/buttons';

import Graph from './Graph';

class WrapGraph extends Component {
    constructor(props){
        super(props)
        this.changeOptions = this.changeOptions.bind(this);
        this.state={
            isEdit: props.edit || false,
            options: props.options,
        }
        this.cancel = eventHandler(this.cancel.bind(this));
        this.save = eventHandler(this.save.bind(this));
        this.destroy = eventHandler(this.destroy.bind(this));
    }
    changeOptions(options){
        this.setState({options: options})
    }
    cancel(){
        this.setState({
            isEdit: false, 
            options: this.props.options
        });
    }
    save(){
        this.setState({isEdit: false});
        this.props.save(this.state.options);
    }
    destroy(){
        this.cancel();
        this.props.destroy(this.props.options);
    }
    render(){
        let graphOptions = this.props.packer(this.state.options)
        let g= <div className={ConstantsCss.Message.Warning}>Graph not configured well</div>
        if (graphOptions){
            g = <Graph data={this.props.data} options={graphOptions} />
        }
        if (this.state.isEdit){
            let actionsList = [
                <Primary shape="circle" key="save" onClick={this.save}>
                    <Save />
                </Primary>,
                <Danger shape="circle" key="delete" onClick={this.destroy}>
                    <Delete />
                </Danger>,
            ]
            if (this.state.options.id) {
                actionsList = [
                    actionsList[0],
                    <Normal shape="circle" key="cancel" onClick={this.cancel}>
                        <Cancel />
                    </Normal>,
                    actionsList[1]
                ]
            }
            return (
                <div className={this.props.className}>
                    <Form config={this.props.graphConfig} onChange={this.changeOptions} options={this.state.options} />
                    {g}
                    {actionsList}
                </div>
                )
        } else {
            return (
                <div className={this.props.className}>
                    {g}
                    <Normal shape="circle" onClick={eventHandler(()=>{this.setState({isEdit: true})})}>
                        <Edit />
                    </Normal>
                </div>
                )
        }
    }
}

export default WrapGraph;