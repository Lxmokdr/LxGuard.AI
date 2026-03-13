"use client"

import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { UploadCloud } from "lucide-react"

interface UploadWizardProps {
    open: boolean
    onOpenChange: (open: boolean) => void
}

export function UploadWizard({ open, onOpenChange }: UploadWizardProps) {
    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>Upload Knowledge Document</DialogTitle>
                    <DialogDescription>
                        Add a new document to the knowledge base. It will be indexed automatically.
                    </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="file" className="text-right">File</Label>
                        <Input id="file" type="file" className="col-span-3" />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="domain" className="text-right">Domain</Label>
                        <Select>
                            <SelectTrigger className="col-span-3">
                                <SelectValue placeholder="Select domain" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="devops">DevOps</SelectItem>
                                <SelectItem value="hr">HR</SelectItem>
                                <SelectItem value="legal">Legal</SelectItem>
                                <SelectItem value="engineering">Engineering</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="access" className="text-right">Access</Label>
                        <Select>
                            <SelectTrigger className="col-span-3">
                                <SelectValue placeholder="Who can view?" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="public">All Employees</SelectItem>
                                <SelectItem value="restricted">Restricted (Admin Only)</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                </div>
                <DialogFooter>
                    <Button type="submit">
                        <UploadCloud className="mr-2 h-4 w-4" />
                        Upload
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}
