import { GraphGroupEnum, GraphKind, GraphV2 } from "../../../api/client/graphs/types";
import { accumulateFn } from "../data-transform/accumulate";

export interface GraphUiRepresentation {
    id?: number;
    name?: string;
    kind?: GraphKind
    tagFilter?: number | null;
    dateRange?: string;
    oldGraph?: number;
    
    groupKind?: GraphGroupEnum
    groupHideOthers?: boolean | null;
    groupTags?: number[]

    horizontalGroupKind?: GraphGroupEnum
    horizontalGroupHideOthers?: boolean | null;
    horizontalGroupTags?: number[]
    horizontalAccumulate?: boolean
}

export const graphToUi = ({group, horizontalGroup, kind, tagFilter, ...graph}: Partial<GraphV2>): GraphUiRepresentation =>({
    ...graph,
    tagFilter: tagFilter ?? undefined,
    kind: kind as GraphKind,
    groupKind: group?.group as GraphGroupEnum,
    groupHideOthers: group?.hideOthers,
    groupTags: group?.groupTags?.map(({tag})=>tag),
    horizontalGroupKind: horizontalGroup?.group as GraphGroupEnum,
    horizontalGroupHideOthers: horizontalGroup?.hideOthers,
    horizontalGroupTags: horizontalGroup?.groupTags?.map(({tag})=>tag),
    horizontalAccumulate: horizontalGroup?.accumulate
})

export const uiToGraph = ({
    groupKind,
    groupHideOthers,
    groupTags,
    horizontalGroupHideOthers,
    horizontalGroupKind,
    horizontalGroupTags,
    horizontalAccumulate,
    oldGraph,
    ...graphUi
}: GraphUiRepresentation): Partial<GraphV2>=> ({
    ...graphUi,
    oldGraph: oldGraph ?? undefined,
    group: groupKind ? {
        group: groupKind,
        hideOthers: groupHideOthers,
        groupTags: groupTags?.map(tag => ({tag}))
    } : undefined,
    horizontalGroup: (horizontalGroupKind && graphUi.kind !== GraphKind.bar) ? {
        group: horizontalGroupKind,
        hideOthers: horizontalGroupHideOthers,
        groupTags: horizontalGroupTags?.map(tag => ({tag})),
        accumulate: horizontalAccumulate
    }: undefined
})